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


def _validated_payload(task: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """Validate task/action and align the API payload with the queued run_id."""
    action = task.get("action")
    if action not in ALLOWED_ACTIONS:
        raise ValueError("Action is not allowlisted.")
    run_id = task.get("run_id")
    if not isinstance(run_id, str) or not run_id.strip():
        raise ValueError("Queued task is missing a valid run_id.")
    raw_payload = task.get("payload", {})
    if not isinstance(raw_payload, dict):
        raise ValueError("Queued task payload must be an object.")
    payload = dict(raw_payload)
    if payload.get("run_id") not in (None, run_id):
        raise ValueError("Payload run_id does not match the queued task run_id.")
    payload["run_id"] = run_id
    if action == "propose_improvement" and not isinstance(payload.get("summary"), str):
        raise ValueError("propose_improvement requires a summary string.")
    if action == "record_checkpoint" and not isinstance(payload.get("tasks"), list):
        raise ValueError("record_checkpoint requires a tasks list.")
    endpoint = {
        "propose_improvement": "/api/agent/evolve/propose",
        "record_checkpoint": "/api/agent/checkpoint",
    }[action]
    return endpoint, payload


def process_task(client: httpx.Client, task: dict[str, Any]) -> dict[str, Any]:
    endpoint, payload = _validated_payload(task)
    response = client.post(endpoint, json=payload, headers=_headers())
    response.raise_for_status()
    return {"action": task["action"], "response": response.json()}


def run_worker(*, max_tasks: int = MAX_TASKS, poll_seconds: float = POLL_SECONDS) -> dict[str, int]:
    """Process at most max_tasks queue items, then exit; suitable for a supervisor."""
    if max_tasks < 1 or max_tasks > 1000:
        raise ValueError("max_tasks must be between 1 and 1000.")
    if poll_seconds < 0 or poll_seconds > 60:
        raise ValueError("poll_seconds must be between 0 and 60.")
    if not 10 <= LEASE_SECONDS <= 600:
        raise ValueError("NOVACOMP_WORKER_LEASE_SECONDS must be between 10 and 600.")
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
            except Exception as exc:
                finish["outcome"] = "failed"
                finish["error"] = f"{type(exc).__name__}: {str(exc)[:500]}"
            finish_response = client.post("/api/queue/finish", json=finish, headers=headers)
            finish_response.raise_for_status()
            if finish["outcome"] == "succeeded":
                stats["succeeded"] += 1
            else:
                stats["failed"] += 1
    return stats


if __name__ == "__main__":
    result = run_worker()
    print("NovaComp worker finished:", result)
