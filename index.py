"""NovaComp Continuity Kernel: stateless API + durable Neon memory.

The API deliberately fails closed: memory endpoints require NOVACOMP_API_TOKEN,
and persistence requires DATABASE_URL. No secrets are hard-coded.
"""
from __future__ import annotations

import hmac
import hashlib
import secrets
import json
import os
from datetime import datetime, timezone
from typing import Any

import psycopg
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from pydantic import BaseModel, Field

from nova_core import (
    TaskSpec, checkpoint_to_dict, make_checkpoint, parallel_waves,
    stable_digest, validate_task_graph,
)
from nova_evolution import Metric, Observation, propose_next_iteration, proposal_to_dict

app = FastAPI(
    title="NovaComp Continuity Kernel",
    version="0.1.0",
    description="Secure, persistent memory and checkpoint API for NovaComp.",
)

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS novacomp_memory (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    category TEXT NOT NULL DEFAULT 'general',
    tags JSONB NOT NULL DEFAULT '[]'::jsonb,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS novacomp_memory_created_at_idx
    ON novacomp_memory (created_at DESC);
CREATE INDEX IF NOT EXISTS novacomp_memory_category_idx
    ON novacomp_memory (category);
CREATE TABLE IF NOT EXISTS novacomp_checkpoints (
    run_id TEXT PRIMARY KEY,
    graph_digest TEXT NOT NULL,
    checkpoint JSONB NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS novacomp_checkpoints_updated_at_idx
    ON novacomp_checkpoints (updated_at DESC);
CREATE TABLE IF NOT EXISTS novacomp_evolution_proposals (
    proposal_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    iteration INTEGER NOT NULL CHECK (iteration > 0),
    proposal JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS novacomp_evolution_proposals_run_idx
    ON novacomp_evolution_proposals (run_id, iteration DESC);
CREATE TABLE IF NOT EXISTS novacomp_task_queue (
    task_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    action TEXT NOT NULL CHECK (action IN ('propose_improvement', 'record_checkpoint')),
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    state TEXT NOT NULL DEFAULT 'queued'
        CHECK (state IN ('queued', 'leased', 'succeeded', 'failed', 'needs_review')),
    idempotency_key TEXT UNIQUE,
    attempts INTEGER NOT NULL DEFAULT 0 CHECK (attempts >= 0),
    max_attempts INTEGER NOT NULL DEFAULT 3 CHECK (max_attempts BETWEEN 1 AND 10),
    lease_token_hash TEXT,
    lease_until TIMESTAMPTZ,
    result JSONB,
    last_error TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS novacomp_task_queue_claim_idx
    ON novacomp_task_queue (state, created_at)
    WHERE state = 'queued';
"""


class TaskInput(BaseModel):
    task_id: str = Field(min_length=1, max_length=100)
    action: str = Field(min_length=1, max_length=100)
    payload: dict[str, Any] = Field(default_factory=dict)
    depends_on: list[str] = Field(default_factory=list, max_length=100)
    idempotency_key: str = Field(default="", max_length=200)


class AgentPlanInput(BaseModel):
    run_id: str = Field(min_length=1, max_length=120)
    tasks: list[TaskInput] = Field(min_length=1, max_length=100)


class MemoryWrite(BaseModel):
    content: str = Field(min_length=1, max_length=12000)
    category: str = Field(default="general", min_length=1, max_length=80)
    tags: list[str] = Field(default_factory=list, max_length=30)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CheckpointInput(BaseModel):
    run_id: str = Field(min_length=1, max_length=120)
    tasks: list[TaskInput] = Field(min_length=1, max_length=100)
    completed_task_ids: list[str] = Field(default_factory=list, max_length=100)
    outputs: dict[str, Any] = Field(default_factory=dict)


class MetricInput(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    value: float
    target: float
    direction: str = "higher"


class QueueTaskInput(BaseModel):
    task_id: str = Field(min_length=1, max_length=120)
    run_id: str = Field(min_length=1, max_length=120)
    action: str = Field(pattern=r"^(propose_improvement|record_checkpoint)$")
    payload: dict[str, Any] = Field(default_factory=dict)
    idempotency_key: str = Field(min_length=1, max_length=200)
    max_attempts: int = Field(default=3, ge=1, le=10)


class QueueFinishInput(BaseModel):
    task_id: str = Field(min_length=1, max_length=120)
    lease_token: str = Field(min_length=20, max_length=200)
    outcome: str = Field(pattern=r"^(succeeded|failed|needs_review)$")
    result: dict[str, Any] = Field(default_factory=dict)
    error: str = Field(default="", max_length=2000)


class EvolutionInput(BaseModel):
    run_id: str = Field(min_length=1, max_length=120)
    summary: str = Field(min_length=1, max_length=2000)
    metrics: list[MetricInput] = Field(default_factory=list, max_length=50)
    known_failures: list[str] = Field(default_factory=list, max_length=30)
    iteration: int = Field(default=1, ge=1, le=5)
    max_iterations: int = Field(default=5, ge=1, le=5)


def require_token(authorization: str | None = Header(default=None)) -> None:
    expected = os.getenv("NOVACOMP_API_TOKEN", "")
    if not expected:
        raise HTTPException(status_code=503, detail="Memory API is not configured.")
    supplied = authorization or ""
    if not hmac.compare_digest(supplied, f"Bearer {expected}"):
        raise HTTPException(status_code=401, detail="Unauthorized.")


def connect_db():
    dsn = os.getenv("DATABASE_URL", "")
    if not dsn:
        raise HTTPException(status_code=503, detail="Persistent storage is not configured.")
    try:
        return psycopg.connect(dsn, connect_timeout=5)
    except Exception:
        # Do not return DSN or provider internals to callers.
        raise HTTPException(status_code=503, detail="Persistent storage is temporarily unavailable.")


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": "NovaComp Continuity Kernel",
        "status": "online",
        "purpose": "secure memory and task continuity",
        "docs": "/docs",
    }


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "novacomp-continuity-kernel",
        "version": app.version,
        "database_configured": bool(os.getenv("DATABASE_URL")),
        "memory_auth_configured": bool(os.getenv("NOVACOMP_API_TOKEN")),
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/api/agent/plan", dependencies=[Depends(require_token)])
def plan_agent_run(request: AgentPlanInput) -> dict[str, Any]:
    """Validate a task DAG and return deterministic, dependency-safe parallel waves."""
    tasks = [
        TaskSpec(
            task_id=task.task_id,
            action=task.action,
            payload=task.payload,
            depends_on=tuple(task.depends_on),
            idempotency_key=task.idempotency_key,
        )
        for task in request.tasks
    ]
    try:
        graph = validate_task_graph(tasks)
        waves = parallel_waves(tasks)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    canonical = [
        {"task_id": t.task_id, "action": t.action, "payload": t.payload,
         "depends_on": list(t.depends_on), "idempotency_key": t.idempotency_key}
        for t in sorted(graph.values(), key=lambda item: item.task_id)
    ]
    return {
        "run_id": request.run_id,
        "validated": True,
        "task_count": len(graph),
        "parallel_waves": waves,
        "graph_digest": stable_digest(canonical),
        "execution_started": False,
        "note": "Planning only: this endpoint does not execute tools or create a durable queue.",
    }


@app.post("/api/agent/checkpoint", dependencies=[Depends(require_token)])
def save_agent_checkpoint(request: CheckpointInput) -> dict[str, Any]:
    """Persist a versioned run checkpoint; refuse to overwrite a different task graph."""
    tasks = [
        TaskSpec(
            task_id=task.task_id,
            action=task.action,
            payload=task.payload,
            depends_on=tuple(task.depends_on),
            idempotency_key=task.idempotency_key,
        )
        for task in request.tasks
    ]
    try:
        checkpoint = make_checkpoint(
            request.run_id, tasks, request.completed_task_ids, request.outputs
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    payload = checkpoint_to_dict(checkpoint)
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute(SCHEMA_SQL)
            cur.execute(
                """
                INSERT INTO novacomp_checkpoints (run_id, graph_digest, checkpoint)
                VALUES (%s, %s, %s::jsonb)
                ON CONFLICT (run_id) DO UPDATE
                SET checkpoint = EXCLUDED.checkpoint,
                    updated_at = NOW()
                WHERE novacomp_checkpoints.graph_digest = EXCLUDED.graph_digest
                RETURNING run_id, graph_digest, updated_at
                """,
                (request.run_id, checkpoint.graph_digest, json.dumps(payload)),
            )
            row = cur.fetchone()
            if row is None:
                raise HTTPException(
                    status_code=409,
                    detail="This run_id already belongs to a different task graph.",
                )
    return {
        "stored": True,
        "run_id": row[0],
        "graph_digest": row[1],
        "checkpoint": payload,
        "updated_at": row[2].isoformat(),
    }


@app.get("/api/agent/checkpoint/{run_id}", dependencies=[Depends(require_token)])
def load_agent_checkpoint(run_id: str) -> dict[str, Any]:
    """Load the last durable checkpoint for a run so an executor can resume it."""
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute(SCHEMA_SQL)
            cur.execute(
                """
                SELECT checkpoint, graph_digest, updated_at
                FROM novacomp_checkpoints
                WHERE run_id = %s
                """,
                (run_id,),
            )
            row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Checkpoint not found.")
    return {
        "found": True,
        "run_id": run_id,
        "checkpoint": row[0],
        "graph_digest": row[1],
        "updated_at": row[2].isoformat(),
    }


@app.post("/api/agent/evolve/propose", dependencies=[Depends(require_token)])
def propose_evolution(request: EvolutionInput) -> dict[str, Any]:
    """Create and persist one bounded improvement proposal from observed evidence."""
    try:
        observation = Observation(
            run_id=request.run_id,
            summary=request.summary,
            metrics=tuple(
                Metric(name=m.name, value=m.value, target=m.target, direction=m.direction)
                for m in request.metrics
            ),
            known_failures=tuple(request.known_failures),
        )
        proposal = propose_next_iteration(
            observation,
            iteration=request.iteration,
            max_iterations=request.max_iterations,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    payload = proposal_to_dict(proposal)
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute(SCHEMA_SQL)
            cur.execute(
                """
                INSERT INTO novacomp_evolution_proposals
                    (proposal_id, run_id, iteration, proposal)
                VALUES (%s, %s, %s, %s::jsonb)
                ON CONFLICT (proposal_id) DO NOTHING
                RETURNING proposal_id
                """,
                (proposal.proposal_id, request.run_id, request.iteration, json.dumps(payload)),
            )
            stored = cur.fetchone() is not None
            if not stored:
                cur.execute(
                    "SELECT proposal FROM novacomp_evolution_proposals WHERE proposal_id = %s",
                    (proposal.proposal_id,),
                )
                existing = cur.fetchone()
                if existing is None:
                    raise HTTPException(status_code=503, detail="Could not confirm stored proposal.")
                payload = existing[0]
    return {
        "stored": True,
        "created_now": stored,
        "proposal": payload,
        "execution_started": False,
        "note": "Proposal only; no source code is modified and no tools are executed.",
    }


@app.get("/api/agent/evolve/proposals/{run_id}", dependencies=[Depends(require_token)])
def list_evolution_proposals(run_id: str, limit: int = Query(default=10, ge=1, le=50)) -> dict[str, Any]:
    """Return recent improvement proposals for one run, newest iteration first."""
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute(SCHEMA_SQL)
            cur.execute(
                """
                SELECT proposal_id, iteration, proposal, created_at
                FROM novacomp_evolution_proposals
                WHERE run_id = %s
                ORDER BY iteration DESC, created_at DESC
                LIMIT %s
                """,
                (run_id, limit),
            )
            rows = cur.fetchall()
    return {
        "run_id": run_id,
        "count": len(rows),
        "proposals": [
            {"proposal_id": row[0], "iteration": row[1], "proposal": row[2], "created_at": row[3].isoformat()}
            for row in rows
        ],
    }


@app.post("/api/queue/enqueue", dependencies=[Depends(require_token)])
def enqueue_task(request: QueueTaskInput) -> dict[str, Any]:
    """Persist an allowlisted task; enqueueing never executes it."""
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute(SCHEMA_SQL)
            cur.execute(
                """
                INSERT INTO novacomp_task_queue
                    (task_id, run_id, action, payload, idempotency_key, max_attempts)
                VALUES (%s, %s, %s, %s::jsonb, %s, %s)
                ON CONFLICT (idempotency_key) DO NOTHING
                RETURNING task_id, state, created_at
                """,
                (request.task_id, request.run_id, request.action,
                 json.dumps(request.payload), request.idempotency_key, request.max_attempts),
            )
            row = cur.fetchone()
            created_now = row is not None
            if row is None:
                cur.execute(
                    """SELECT task_id, state, created_at FROM novacomp_task_queue
                       WHERE idempotency_key = %s""",
                    (request.idempotency_key,),
                )
                row = cur.fetchone()
                if row is None:
                    raise HTTPException(status_code=503, detail="Could not confirm queued task.")
                if row[0] != request.task_id:
                    raise HTTPException(status_code=409, detail="Idempotency key belongs to another task.")
    return {"stored": True, "created_now": created_now,
            "task_id": row[0], "state": row[1], "created_at": row[2].isoformat(),
            "execution_started": False}


@app.post("/api/queue/claim", dependencies=[Depends(require_token)])
def claim_task(lease_seconds: int = Query(default=90, ge=10, le=600)) -> dict[str, Any]:
    """Lease one queued task for a separate worker; never runs the task in the API."""
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute(SCHEMA_SQL)
            cur.execute(
                """
                UPDATE novacomp_task_queue
                SET state = CASE WHEN attempts >= max_attempts THEN 'failed' ELSE 'queued' END,
                    lease_token_hash = NULL, lease_until = NULL,
                    last_error = COALESCE(last_error, 'Lease expired before completion.'),
                    updated_at = NOW()
                WHERE state = 'leased' AND lease_until <= NOW()
                """
            )
            cur.execute(
                """
                WITH candidate AS (
                    SELECT task_id FROM novacomp_task_queue
                    WHERE state = 'queued' AND attempts < max_attempts
                    ORDER BY created_at, task_id
                    FOR UPDATE SKIP LOCKED LIMIT 1
                )
                UPDATE novacomp_task_queue AS q
                SET state = 'leased', attempts = attempts + 1,
                    lease_token_hash = %s,
                    lease_until = NOW() + (%s * INTERVAL '1 second'),
                    updated_at = NOW()
                FROM candidate
                WHERE q.task_id = candidate.task_id
                RETURNING q.task_id, q.run_id, q.action, q.payload, q.attempts,
                          q.max_attempts, q.lease_until
                """,
                (token_hash, lease_seconds),
            )
            row = cur.fetchone()
    if row is None:
        return {"claimed": False, "task": None}
    return {"claimed": True, "task": {
        "task_id": row[0], "run_id": row[1], "action": row[2], "payload": row[3],
        "attempt": row[4], "max_attempts": row[5], "lease_until": row[6].isoformat(),
        "lease_token": token,
    }, "execution_started": False,
        "note": "A separate allowlisted worker must perform the action and report its outcome."}


@app.post("/api/queue/finish", dependencies=[Depends(require_token)])
def finish_task(request: QueueFinishInput) -> dict[str, Any]:
    """Accept an outcome only from the holder of the active lease token."""
    token_hash = hashlib.sha256(request.lease_token.encode("utf-8")).hexdigest()
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute(SCHEMA_SQL)
            cur.execute(
                """
                UPDATE novacomp_task_queue
                SET state = CASE
                        WHEN %s = 'failed' AND attempts < max_attempts THEN 'queued'
                        ELSE %s
                    END,
                    result = %s::jsonb,
                    last_error = NULLIF(%s, ''),
                    lease_token_hash = NULL,
                    lease_until = NULL,
                    updated_at = NOW()
                WHERE task_id = %s AND state = 'leased'
                  AND lease_token_hash = %s AND lease_until > NOW()
                RETURNING task_id, state, attempts
                """,
                (request.outcome, request.outcome, json.dumps(request.result), request.error,
                 request.task_id, token_hash),
            )
            row = cur.fetchone()
    if row is None:
        raise HTTPException(status_code=409, detail="Lease invalid, expired, or task is not leased.")
    return {"updated": True, "task_id": row[0], "state": row[1], "attempts": row[2]}


@app.get("/api/queue/status", dependencies=[Depends(require_token)])
def queue_status() -> dict[str, Any]:
    """Summarize durable queue state without exposing payloads or lease tokens."""
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute(SCHEMA_SQL)
            cur.execute(
                "SELECT state, COUNT(*) FROM novacomp_task_queue GROUP BY state ORDER BY state"
            )
            rows = cur.fetchall()
    return {"states": {row[0]: row[1] for row in rows}, "automatic_execution": False}


@app.get("/api/capabilities")
def capabilities() -> dict[str, Any]:
    return {
        "architecture": "stateless API + optional PostgreSQL persistence",
        "capabilities": [
            "authenticated memory writes",
            "keyword retrieval with category filtering",
            "deterministic dependency-aware parallel task planning",
            "tool risk-policy primitives and checkpoint serialization library",
            "durable checkpoint save/load API (requires configured PostgreSQL)",
            "bounded evidence-based recursive improvement proposals with durable history",
            "durable idempotent task queue with expiring leases and authenticated completion",
            "health diagnostics",
        ],
        "not_claimed": [
            "consciousness",
            "semantic embeddings (not yet connected)",
            "durable checkpoint persistence until DATABASE_URL is configured and tested",
            "durable queue is API-connected but requires a separate worker process for execution",
            "automatic tool execution or continuous background execution",
            "successful database connection until tested",
        ],
    }


@app.post("/api/memory", dependencies=[Depends(require_token)])
def store_memory(item: MemoryWrite) -> dict[str, Any]:
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute(SCHEMA_SQL)
            cur.execute(
                """
                INSERT INTO novacomp_memory (content, category, tags, metadata)
                VALUES (%s, %s, %s::jsonb, %s::jsonb)
                RETURNING id, category, tags, created_at
                """,
                (
                    item.content,
                    item.category,
                    json.dumps(list(dict.fromkeys(item.tags))),
                    json.dumps(item.metadata),
                ),
            )
            row = cur.fetchone()
    return {
        "stored": True,
        "id": row[0],
        "category": row[1],
        "tags": row[2],
        "created_at": row[3].isoformat(),
    }


@app.get("/api/memory/search", dependencies=[Depends(require_token)])
def search_memory(
    q: str = Query(min_length=1, max_length=300),
    category: str | None = Query(default=None, max_length=80),
    limit: int = Query(default=10, ge=1, le=50),
) -> dict[str, Any]:
    # Baseline hybrid-friendly retrieval: lexical match + recency.
    # Embedding retrieval can be added later without changing the API contract.
    pattern = f"%{q}%"
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute(SCHEMA_SQL)
            if category:
                cur.execute(
                    """
                    SELECT id, content, category, tags, metadata, created_at
                    FROM novacomp_memory
                    WHERE (content ILIKE %s OR tags::text ILIKE %s)
                      AND category = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                    """,
                    (pattern, pattern, category, limit),
                )
            else:
                cur.execute(
                    """
                    SELECT id, content, category, tags, metadata, created_at
                    FROM novacomp_memory
                    WHERE content ILIKE %s OR tags::text ILIKE %s
                    ORDER BY created_at DESC
                    LIMIT %s
                    """,
                    (pattern, pattern, limit),
                )
            rows = cur.fetchall()
    return {
        "query": q,
        "count": len(rows),
        "items": [
            {
                "id": row[0],
                "content": row[1],
                "category": row[2],
                "tags": row[3],
                "metadata": row[4],
                "created_at": row[5].isoformat(),
            }
            for row in rows
        ],
    }
