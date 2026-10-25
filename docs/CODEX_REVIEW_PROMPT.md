# Codex implementation and verification prompt

Connect Codex to suryamayaharum-droid/novacomp and ask it to perform a source-grounded review of the current main branch.

> Review the NovaComp FastAPI API and bounded queue worker. Read AGENTS.md if present, NOVA_STATUS.md, docs/PRODUCTION_RUNBOOK.md, index.py, nova_core.py, nova_evolution.py, nova_worker.py, and all tests. Do not claim access to production secrets. Do not read or print secret values. Do not connect to or mutate a production database.
>
> Run python -m pip install -e '.[test]' and python -m unittest discover -s tests -v. Check the worker's retry/lease semantics, exception sanitization, graceful shutdown, idempotency, and schema creation behavior. Add focused tests for every bug found. Check whether API endpoints return correct statuses when DATABASE_URL is missing/unreachable and whether errors leak DSNs/tokens. Review dependency declarations and the worker container build.
>
> Do not add GitHub Actions. Do not introduce arbitrary shell execution, autonomous source editing, or automatic production deployment. Make changes on a separate branch or worktree, show a concise diff, run tests again, and report exact command output, commit SHA, and what remains blocked by production environment variables or deployment protection. Do not merge or deploy until the owner reviews the changes.
