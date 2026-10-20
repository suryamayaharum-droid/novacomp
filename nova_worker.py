"""Bounded external worker for NovaComp's durable queue.

Run as a separately supervised process. It only dispatches the two API-backed,
allowlisted actions; it does not execute shell commands or edit source code.
"""
from __future__ import annotations

import os
import time
from typing import Any

import httpx

API_URL = os.getenv("NOVACOMP_API_URL", "").rstrip("/")
API_TOKEN = os.getenv("NOVACOMP_API_TOKEN", "")
MAX_TASKS = int(os.getenv("NOVACOMP_WORKER_MAX_TASKS", "10"))
POLL_SECONDS = float(os.getenv("NOVACOMP_WORKER_POLL_SECONDS", "2"))
LEASE_SECONDS = int(os.getenv("NOVACOMP_WORKER_LEASE_SECONDS", "90"))
ALLOWED_ACTIONS = {"propose_improvement", "record_checkpoint"}


def _headers() -> dict[str, str]:
    if not API_URL or not API_TOKEN:
        raise RuntimeError("NOVACOMP_API_URL and NOVACOMP_API_TOKEN must be configured.")
    return {"Authorization": f"Bearer {API_TOKEN}"}


def process_task(client: httpx.Client, task: dict[str, Any]) -> dict[str, Any]:
    action = task.get("action")
    if action not in ALLOWED_ACTIONS:
        raise ValueError("Action is not allowlisted.")
    endpoint = {
        "propose_improvement": "/api/agent/evolve/propose",
        "record_checkpoint": "/api/agent/checkpoint",
    }[action]
    response = client.post(endpoint, json=task.get("payload", {}), headers=_headers())
    response.raise_for_status()
    body = response.json()
    return {"action": action, "response": body}


def run_worker(*, max_tasks: int = MAX_TASKS, poll_seconds: float = POLL_SECONDS) -> dict[str, int]:
    """Process at most max_tasks queue items, then exit; suitable for a supervisor."""
    if max_tasks < 1 or max_tasks > 1000:
        raise ValueError("max_tasks must be between 1 and 1000.")
    if poll_seconds < 0 or poll_seconds > 60:
        raise ValueError("poll_seconds must be between 0 and 60.")
    headers = _headers()
    stats = {"claimed": 0, "succeeded": 0, "failed": 0, "idle_polls": 0}
    with httpx.Client(base_url=API_URL, timeout=20.0, follow_redirects=False) as client:
        for _ in range(max_tasks):
            claimed_response = client.post(
                "/api/queue/claim",
                params={"lease_seconds": LEASE_SECONDS},
                headers=headers,
            )
            claimed_response.raise_for_status()
            envelope = claimed_response.json()
            if not envelope.get("claimed"):
                stats["idle_polls"] += 1
                if poll_seconds:
                    time.sleep(poll_seconds)
                # Bounded idle handling: no endless polling loop.
                continue
            task = envelope["task"]
            stats["claimed"] += 1
            finish: dict[str, Any] = {
                "task_id": task["task_id"],
                "lease_token": task["lease_token"],
                "outcome": "succeeded",
                "result": {},
                "error": "",
            }
            try:
                finish["result"] = process_task(client, task)
                stats["succeeded"] += 1
            except Exception as exc:
                finish["outcome"] = "failed"
                # Keep only a short exception summary; never include request headers.
                finish["error"] = f"{type(exc).__name__}: {str(exc)[:500]}"
                stats["failed"] += 1
            finish_response = client.post("/api/queue/finish", json=finish, headers=headers)
            finish_response.raise_for_status()
    return stats


if __name__ == "__main__":
    result = run_worker()
    print("NovaComp worker finished:", result)
