"""NovaComp Continuity Kernel: stateless API + durable Neon memory.

The API deliberately fails closed: memory endpoints require NOVACOMP_API_TOKEN,
and persistence requires DATABASE_URL. No secrets are hard-coded.
"""
from __future__ import annotations

import hmac
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


@app.get("/api/capabilities")
def capabilities() -> dict[str, Any]:
    return {
        "architecture": "stateless API + optional PostgreSQL persistence",
        "capabilities": [
            "authenticated memory writes",
            "keyword retrieval with category filtering",
            "deterministic dependency-aware parallel task planning",
            "tool risk-policy primitives and checkpoint serialization library",
            "health diagnostics",
        ],
        "not_claimed": [
            "consciousness",
            "semantic embeddings (not yet connected)",
            "durable task queue/checkpoint storage (not yet connected)",
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
