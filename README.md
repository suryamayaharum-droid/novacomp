# NovaComp — Continuity Kernel

NovaComp is a bounded FastAPI service for persistent memory, task-graph planning, resumable checkpoints, evidence-based improvement proposals, and a durable queue for a separately supervised worker.

## Current, verified scope

- Stateless FastAPI API deployed on Vercel.
- PostgreSQL persistence is supported when a dedicated `DATABASE_URL` is configured and reachable.
- Bearer-token authentication for memory, checkpoints, queue, and proposal endpoints via `NOVACOMP_API_TOKEN`.
- Deterministic task-graph validation and parallel-wave planning.
- Checkpoint save/load with task-graph digest protection.
- Evidence-based improvement proposals; proposals do not edit source code or self-deploy.
- Idempotent task queue with bounded allowlisted actions, expiring leases, retry limits, and authenticated completion.
- Bounded queue worker supports one-shot execution or continuous supervised mode.
- Read-only smoke test and deployment runbook.

## Not claimed

- No consciousness or self-directed general intelligence.
- No semantic embeddings/vector search wired into the current API; memory retrieval is lexical.
- No automatic source-code mutation or arbitrary shell execution.
- No continuously running worker unless a separate worker service is deployed.
- No Ollama/model runtime bundled into the Vercel API.
- Persistent production storage is not considered healthy until the health endpoint reports both database configuration and reachability.

## Architecture

- `index.py`: FastAPI routes, authentication, database schema and persistence.
- `nova_core.py`: deterministic task graph validation, policy primitives, checkpoints.
- `nova_evolution.py`: bounded proposals from explicit observations; execution remains disabled.
- `nova_worker.py`: external worker for only `propose_improvement` and `record_checkpoint`.
- `Dockerfile.worker`: container entrypoint for a supervised worker host.
- `scripts/smoke_test.py`: read-only endpoint checks.
- `docs/PRODUCTION_RUNBOOK.md`: production environment, worker, and validation procedure.
- `docs/CODEX_REVIEW_PROMPT.md`: prompt for an independent Codex review.

## API

- `GET /`: service identity and docs location.
- `GET /api/health`: liveness, environment configuration presence, and real PostgreSQL reachability.
- `GET /api/capabilities`: capability and limitation declaration.
- `GET /openapi.json`: generated API schema.
- `POST /api/agent/plan`: validate task graph and return parallel waves (does not execute tasks).
- `POST /api/agent/checkpoint`, `GET /api/agent/checkpoint/{run_id}`: persist/load checkpoints.
- `POST /api/agent/evolve/propose`, `GET /api/agent/evolve/proposals/{run_id}`: create/list bounded proposals.
- `POST /api/queue/enqueue`, `POST /api/queue/claim`, `POST /api/queue/finish`, `GET /api/queue/status`: durable queue lifecycle.
- `POST /api/memory`, `GET /api/memory/search`: store and lexically retrieve memory.

Authenticated routes require `Authorization: Bearer <NOVACOMP_API_TOKEN>`. Never place secrets in source control or send them through chat.

## Local development and tests

Requires Python 3.10+.

```bash
python -m pip install -e '.[test]'
python -m unittest discover -s tests -v
```

Run a read-only deployment check:

```bash
NOVACOMP_BASE_URL=https://novacomp.vercel.app python scripts/smoke_test.py
```

The check must run from a network/session authorized to access the deployment. Vercel SSO or deployment protection may block unauthenticated access.

## Worker

One batch:

```bash
python nova_worker.py
```

Continuous supervised mode:

```bash
python nova_worker.py --continuous
```

Set `NOVACOMP_API_URL` and `NOVACOMP_API_TOKEN` in the worker host's secret manager. The worker handles SIGTERM/SIGINT and limits actions to the allowlist. Use a process/container host that restarts failed services; Vercel Functions are not a persistent daemon.

## Production status

See [NOVA_STATUS.md](NOVA_STATUS.md) and [the production runbook](docs/PRODUCTION_RUNBOOK.md). Do not treat a successful Vercel build as proof of a healthy production database or running worker.
