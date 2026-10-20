# NovaComp V2 — architecture and safety gates

Updated: 2026-10-19

## Observed state

- Vercel project: `novacomp`, configured as FastAPI.
- A deployment from commit `96fbfd9` reached Vercel state `READY` after changing the project framework/build detection.
- The deployed host currently requires Vercel login/SSO, so external HTTP verification through an unauthenticated fetch is blocked. READY means the build/deployment pipeline completed, not that the endpoints or database have passed runtime tests.
- Vercel project environment list is empty: no `DATABASE_URL` or `NOVACOMP_API_TOKEN` is configured.
- The connected Neon project has two listed branches; both are archived. Do not point the service at them until an active branch/endpoint is deliberately restored and verified.
- The attempted pyproject dependency update was blocked by the platform's safety controls and is not considered applied. Verify that runtime dependencies are explicitly declared before treating the API as runnable.

## V2 architecture: Continuity Kernel

### Layer 1 — request gateway
FastAPI endpoints, strict Pydantic input limits, bearer-token verification using constant-time comparison, bounded queries, generic errors, and no secret values in logs or responses.

### Layer 2 — durable event ledger
PostgreSQL records append-only events and snapshots. Use separate tables for:
- `memory_items`: content, category, tags, importance, provenance, created_at, updated_at.
- `task_runs`: idempotency key, goal, state, attempt count, lease expiry, created_at, updated_at.
- `checkpoints`: task_id, step, state JSON, source revision, timestamp.
- `audit_events`: actor, action, resource ID, outcome, timestamp; never record credentials or full sensitive payloads.

Prefer schema migrations run explicitly rather than running DDL on every API request. Create a least-privilege database role. Never run destructive migrations automatically.

### Layer 3 — retrieval
Stage 1: PostgreSQL full-text/ILIKE retrieval, category/tag filters, importance and recency.
Stage 2: embeddings and vector distance using pgvector if the chosen Neon configuration supports it.
Stage 3: hybrid ranking via reciprocal-rank fusion of lexical, vector, tag, importance and recency scores. Store the embedding model/version with each vector. Retrieval must return source IDs and confidence signals; low-confidence matches should be labelled, not presented as fact.

### Layer 4 — controlled task engine
A task is a durable state machine: `queued -> leased -> running -> succeeded | failed | needs_review`.
- Idempotency keys prevent duplicate writes.
- Lease expiry enables safe recovery after a worker dies.
- Bounded retries with exponential backoff; no infinite loops.
- Human approval required for public publishing, destructive changes, spending, secret rotation, or permissions changes.
- Every run writes a checkpoint and a concise outcome.
- Serverless requests are not background daemons. A scheduled worker or separately hosted process is required for autonomous recurring work.

### Layer 5 — tools and adapters
GitHub adapter for read/review/commit workflows; Vercel adapter for deployment status; Neon adapter for durable records; later, an authenticated OpenClaw/MCP adapter. Each adapter receives narrow permissions and exposes typed actions, never an unrestricted shell.

## Security requirements

- Keep `DATABASE_URL` and `NOVACOMP_API_TOKEN` server-side only.
- Use a high-entropy bearer token stored in Vercel's encrypted environment configuration, never in source control, browser JavaScript, or chat.
- Use separate Preview and Production secrets where possible.
- Restrict the database role to the schema and operations needed.
- Rate-limit public endpoints and cap request size.
- Never expose an arbitrary SQL endpoint or arbitrary command execution.
- Use synthetic data for validation. Do not import personal memories until authentication, access controls, backups and restore have been tested.
- Keep SSO/protection enabled until an authorized private test route is available; do not weaken access protection merely to make a fetch test pass.

## Release gates

1. Correct and verify package/runtime dependency declaration.
2. Create or select a non-archived Neon branch; verify compute, database and role.
3. Configure server-side environment variables through Vercel UI/API without printing values.
4. Deploy a Preview while automatic Git deployments remain disabled.
5. Authenticated tests: no token -> 401/503 as designed; wrong token -> 401; valid synthetic write -> ID; search -> same synthetic item.
6. Confirm persistence after a new deployment and after an explicit process restart.
7. Confirm logs contain no secrets; test backup/restore.
8. Only then connect OpenClaw and record measured recovery latency.

## Honest capability model

The system is an engineered assistant service, not an independent conscious entity. Track concrete measures instead:
- durable write/read pass rate;
- recovery after restart;
- task completion and retry rates;
- source-backed retrieval accuracy;
- cost per successful task;
- unauthorized request rejection;
- recovery time from the last checkpoint.

Do not report a percentage of consciousness. Report only measured milestones and reproducible tests.
