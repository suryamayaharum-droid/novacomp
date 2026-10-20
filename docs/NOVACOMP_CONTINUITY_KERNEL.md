# NovaComp Continuity Kernel — integration notes

## Goal

Join the existing NovaComp project to a practical, testable persistence layer:
- **Vercel / FastAPI** runs request-scoped API operations; it is not a permanent daemon.
- **Neon / PostgreSQL** stores durable memory across function restarts.
- **GitHub** stores source, architecture decisions, and recovery instructions.
- **OpenClaw / MCP** can call this API later through an authenticated adapter, after the API has been deployed and verified.

This is a continuity kernel, not a claim of consciousness or unrestricted autonomy.

## API

- `GET /`: service identity
- `GET /api/health`: configuration-only health (does not test database connectivity)
- `GET /api/capabilities`: current capabilities and explicit limitations
- `POST /api/memory`: authenticated persistent write
- `GET /api/memory/search?q=...`: authenticated lexical retrieval, optionally filtered by category
- `/docs`: FastAPI schema

Memory endpoints require `Authorization: Bearer <NOVACOMP_API_TOKEN>`. If the token or database DSN is absent, the service fails closed. Never place credentials in GitHub or in public frontend code.

## Required deployment configuration

In the Vercel project settings, configure these server-side environment variables:
1. `DATABASE_URL`: Neon pooled PostgreSQL connection string for a dedicated database role with only the permissions this service needs.
2. `NOVACOMP_API_TOKEN`: a high-entropy random token. Generate it locally or in a password manager; do not send it in chat.

Use Preview first. Verify `GET /api/health`, then write and retrieve a synthetic non-sensitive test record with the token. Confirm restart/redeploy persistence before adding real memories. The current connected Neon project's default branch was observed as archived, so verify/restore a usable branch in the Neon console before setting `DATABASE_URL`; do not assume the old connection is ready.

## Security and deployment gates

- Git-triggered deployment remains disabled in `vercel.json` so this repair does not silently publish new production code.
- This repository's current Vercel deployment was observed in ERROR state because of an invalid `vercel.json`.
- After reviewing the code and adding environment variables, trigger a Preview deployment explicitly from Vercel.
- Keep the token server-side; rotate it if exposed.
- Do not expose PostgreSQL credentials, MCP ports, or an unrestricted shell endpoint.
- Do not enable arbitrary command execution through this API.
- Back up data and test restore before using this for important project memory.

## Current retrieval design and next evolution

The first version uses PostgreSQL durability with case-insensitive keyword/tag retrieval and recency ordering. This is intentionally honest and easy to test. It does **not** yet perform semantic vector retrieval. The next compatible stage is:
1. add embeddings from a selected embedding provider or a local embedding model;
2. store vectors using pgvector if available, otherwise a separate vector store;
3. combine lexical rank, vector similarity, tags, importance, and recency (reciprocal-rank fusion);
4. add task/checkpoint tables with idempotency keys and lease-based workers;
5. connect OpenClaw via a small authenticated MCP adapter, after checking the current OpenClaw MCP transport and deployment constraints.

## Validation checklist

- [ ] Vercel Preview build succeeds.
- [ ] Health endpoint responds.
- [ ] Missing token returns 503 for memory endpoints; wrong token returns 401.
- [ ] Synthetic memory write returns an ID.
- [ ] Search finds the synthetic memory.
- [ ] Data remains after redeployment/restart.
- [ ] Logs contain no secrets.
- [ ] Only after these pass: connect OpenClaw and measure recovery latency.
