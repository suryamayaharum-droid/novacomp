# NovaComp — Durable Queue and Safe Evolution

## What changed

The API now exposes a PostgreSQL-backed task queue with idempotent enqueueing,
short-lived leases, retry limits, hashed lease-token validation, and status counts.
Claims use `FOR UPDATE SKIP LOCKED` so concurrent workers do not claim the same
queued row at the same time.

## Endpoints

All endpoints below require `Authorization: Bearer <NOVACOMP_API_TOKEN>`.

- `POST /api/queue/enqueue`: enqueue one task. The action must be exactly
  `propose_improvement` or `record_checkpoint`. The idempotency key is unique.
- `POST /api/queue/claim?lease_seconds=90`: claim one task for a separate worker.
  The response includes a one-time lease token; store it only in worker memory.
- `POST /api/queue/finish`: report `succeeded`, `failed`, or `needs_review`.
  The task must still have a valid, unexpired lease.
- `GET /api/queue/status`: count tasks by state without exposing payloads.

Expired leases are reclaimed during the next claim request. A task that has used
all attempts is marked failed instead of being retried forever.

## Safety boundary

This queue is **durable coordination**, not a running autonomous worker. The API
does not execute arbitrary Python, shell commands, deployments, external writes,
or code edits. A separate worker process must be deployed and operated before
queued tasks can be processed. That worker must independently validate each
payload, implement only the two allowlisted actions, record bounded results, and
route ambiguous or external-impacting actions to human review.

The evolution planner still generates evidence-based proposals with
`execution_allowed = false`. Queueing a proposal does not approve or execute it.

## Next validation steps

1. Verify the deployment build and call `/api/health` and `/api/capabilities`.
2. With a valid API token, enqueue a test task and repeat the same request to
   confirm idempotency.
3. Claim the task, confirm a second concurrent claim does not return that task,
   and test completion with both valid and invalid lease tokens.
4. Test expiry/retry behavior and max-attempt termination.
5. Run the repository test suite before enabling any worker.
6. Add a separate supervised worker only after these checks pass; do not use an
   unbounded recursive loop or arbitrary-code execution.

## Operational limitation

Vercel API functions are request-driven and should not be treated as a permanent
background process. A separate supervised runtime or managed queue worker is
required for continuous processing. No GitHub Actions workflow is required by
this design.
