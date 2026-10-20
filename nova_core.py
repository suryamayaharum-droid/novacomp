"""NovaComp native orchestration primitives.

This module is deliberately deterministic: it validates task graphs, computes
parallel execution waves, enforces tool policy, and emits resumable checkpoints.
It does not run forever or execute arbitrary code by itself.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Iterable


class Risk(str, Enum):
    READ = "read"
    REVERSIBLE = "reversible"
    EXTERNAL_WRITE = "external_write"
    DESTRUCTIVE = "destructive"


class TaskState(str, Enum):
    QUEUED = "queued"
    LEASED = "leased"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    NEEDS_REVIEW = "needs_review"


_ALLOWED_TRANSITIONS = {
    TaskState.QUEUED: {TaskState.LEASED, TaskState.NEEDS_REVIEW},
    TaskState.LEASED: {TaskState.RUNNING, TaskState.QUEUED, TaskState.FAILED},
    TaskState.RUNNING: {TaskState.SUCCEEDED, TaskState.FAILED, TaskState.NEEDS_REVIEW},
    TaskState.SUCCEEDED: set(),
    TaskState.FAILED: {TaskState.QUEUED, TaskState.NEEDS_REVIEW},
    TaskState.NEEDS_REVIEW: {TaskState.QUEUED, TaskState.FAILED},
}


@dataclass(frozen=True)
class ToolPolicy:
    name: str
    risk: Risk
    enabled: bool = True
    requires_approval: bool = False


@dataclass(frozen=True)
class TaskSpec:
    task_id: str
    action: str
    payload: dict[str, Any] = field(default_factory=dict)
    depends_on: tuple[str, ...] = ()
    idempotency_key: str = ""


@dataclass(frozen=True)
class Checkpoint:
    schema_version: int
    run_id: str
    created_at: str
    completed_task_ids: tuple[str, ...]
    pending_task_ids: tuple[str, ...]
    outputs: dict[str, Any]
    graph_digest: str


class PolicyDenied(PermissionError):
    pass


def stable_digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def validate_task_graph(tasks: Iterable[TaskSpec]) -> dict[str, TaskSpec]:
    """Reject duplicate IDs, missing dependencies, and cycles before execution."""
    by_id: dict[str, TaskSpec] = {}
    for task in tasks:
        if not task.task_id or task.task_id in by_id:
            raise ValueError("Task IDs must be non-empty and unique.")
        if not task.action:
            raise ValueError(f"Task {task.task_id!r} has no action.")
        by_id[task.task_id] = task

    for task in by_id.values():
        missing = set(task.depends_on) - set(by_id)
        if missing:
            raise ValueError(f"Task {task.task_id!r} has missing dependencies: {sorted(missing)}")
        if task.task_id in task.depends_on:
            raise ValueError(f"Task {task.task_id!r} cannot depend on itself.")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(task_id: str) -> None:
        if task_id in visiting:
            raise ValueError("Task graph contains a dependency cycle.")
        if task_id in visited:
            return
        visiting.add(task_id)
        for dependency in by_id[task_id].depends_on:
            visit(dependency)
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in by_id:
        visit(task_id)
    return by_id


def parallel_waves(tasks: Iterable[TaskSpec], completed: Iterable[str] = ()) -> list[list[str]]:
    """Return deterministic dependency-safe waves; each wave can run in parallel."""
    by_id = validate_task_graph(tasks)
    done = set(completed)
    unknown_done = done - set(by_id)
    if unknown_done:
        raise ValueError(f"Checkpoint contains unknown task IDs: {sorted(unknown_done)}")
    waves: list[list[str]] = []
    while len(done) < len(by_id):
        ready = sorted(
            task_id for task_id, task in by_id.items()
            if task_id not in done and set(task.depends_on).issubset(done)
        )
        if not ready:
            raise ValueError("No runnable task remains; graph or checkpoint is inconsistent.")
        waves.append(ready)
        done.update(ready)
    return waves


def authorize_tool(policy: ToolPolicy, *, approval_granted: bool = False) -> None:
    """Fail closed for disabled tools and externally consequential operations."""
    if not policy.enabled:
        raise PolicyDenied(f"Tool {policy.name!r} is disabled by policy.")
    if policy.risk in {Risk.EXTERNAL_WRITE, Risk.DESTRUCTIVE}:
        if not policy.requires_approval or not approval_granted:
            raise PolicyDenied(f"Tool {policy.name!r} requires explicit approval.")
    elif policy.requires_approval and not approval_granted:
        raise PolicyDenied(f"Tool {policy.name!r} requires approval.")


def transition(current: TaskState, target: TaskState) -> TaskState:
    if target not in _ALLOWED_TRANSITIONS[current]:
        raise ValueError(f"Invalid task transition: {current.value} -> {target.value}")
    return target


def make_checkpoint(
    run_id: str,
    tasks: Iterable[TaskSpec],
    completed_task_ids: Iterable[str],
    outputs: dict[str, Any] | None = None,
) -> Checkpoint:
    by_id = validate_task_graph(tasks)
    completed = tuple(sorted(set(completed_task_ids)))
    if set(completed) - set(by_id):
        raise ValueError("Cannot checkpoint task IDs not present in the run.")
    pending = tuple(sorted(set(by_id) - set(completed)))
    graph = [
        {"task_id": t.task_id, "action": t.action, "payload": t.payload,
         "depends_on": list(t.depends_on), "idempotency_key": t.idempotency_key}
        for t in sorted(by_id.values(), key=lambda item: item.task_id)
    ]
    return Checkpoint(
        schema_version=1,
        run_id=run_id,
        created_at=datetime.now(timezone.utc).isoformat(),
        completed_task_ids=completed,
        pending_task_ids=pending,
        outputs=outputs or {},
        graph_digest=stable_digest(graph),
    )


def checkpoint_to_dict(checkpoint: Checkpoint) -> dict[str, Any]:
    """JSON-ready envelope suitable for a durable database or file store."""
    return asdict(checkpoint)
