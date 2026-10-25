# NovaComp production runbook

This runbook distinguishes deployable code from infrastructure that must be provisioned. Do not reuse the shared Arte Harum/Chat database for NovaComp production.

## Components

- API: FastAPI on Vercel (https://novacomp.vercel.app).
- Persistence: a dedicated PostgreSQL database with the schema created by index.py.
- Queue consumer: nova_worker.py --continuous, deployed as a supervised container/background worker.
- Model provider: optional OpenAI-compatible endpoint configured only by server-side environment variables. No provider key is committed to source.
- Codex review: use docs/CODEX_REVIEW_PROMPT.md after connecting the repository in Codex.

## Required production variables

Vercel project → Settings → Environment Variables → Production:

- DATABASE_URL: PostgreSQL URL for a dedicated NovaComp database.
- NOVACOMP_API_TOKEN: random high-entropy bearer token, shared only with the trusted worker.

Worker host environment:

- NOVACOMP_API_URL=https://novacomp.vercel.app
- NOVACOMP_API_TOKEN: same token as the Vercel Production variable.
- Optional tuning: NOVACOMP_WORKER_MAX_TASKS=10, NOVACOMP_WORKER_POLL_SECONDS=2, NOVACOMP_WORKER_LEASE_SECONDS=90, NOVACOMP_WORKER_IDLE_SLEEP_SECONDS=5, NOVACOMP_WORKER_ERROR_BACKOFF_SECONDS=10.

Never put credentials in Git, screenshots, issue descriptions, or chat messages. Use each provider's secret-variable UI. After changing Vercel variables, create a new Production deployment; existing deployments do not inherit later variable changes.

## Provision database safely

1. In the Vercel project, open Storage/Integrations and provision a new Neon database/project dedicated to NovaComp, or use a separately approved PostgreSQL service.
2. Confirm the database is not the existing shared Arte Harum/Chat project.
3. Add its connection URL as DATABASE_URL for Production only.
4. Generate a random token in a password manager or secret manager; add it as NOVACOMP_API_TOKEN in Production and in the worker host's secret store.
5. Deploy the current main branch to Production.

## Deploy worker container

Build Dockerfile.worker from the repository root on a container/background-worker host. Set the worker variables above in that host's secret/configuration panel. The command runs bounded batches continuously, handles SIGTERM/SIGINT, backs off on upstream failures, and logs only sanitized error categories. Select a plan/host explicitly; do not create paid infrastructure without reviewing its price.

The worker only allows propose_improvement and record_checkpoint; it does not run shell commands or edit/publish source code.

## Validation checklist

1. Run python -m pip install -e '.[test]'.
2. Run python -m unittest discover -s tests -v.
3. Run NOVACOMP_BASE_URL=https://novacomp.vercel.app python scripts/smoke_test.py from a network that can access the deployment. If Vercel SSO blocks access, use a properly authorized session; do not disable protection just to make the test pass.
4. Check /api/health: database_configured=true and database_reachable=true.
5. With a secret-safe authorized client, write a uniquely tagged test memory, read it back, and delete it using an approved maintenance procedure if deletion is supported. Never put real private content in test records.
6. Enqueue an allowlisted no-op/checkpoint test, verify worker claim/finish and final queue state, then verify idempotent replay.
7. Confirm the worker stays running and stops cleanly on SIGTERM.
8. Save observed outputs, deployed commit SHA, and unresolved failures in NOVA_STATUS.md.

## Model provider

The API currently provides deterministic planning, persistent memory, checkpoints, bounded improvement proposals, and a durable queue. Those features do not by themselves constitute an LLM inference engine. Add a provider only after choosing an approved endpoint and setting its key securely. Ollama requires a separate machine/container with enough memory/compute; it does not run persistently inside a standard Vercel Function.
