# Phase 0-1 Plan and Checklist

## Plan (concise)
1) Scaffold repo: Docker Compose, FastAPI skeleton, config, and env example.
2) Data layer: Postgres models + Alembic, Neo4j + Qdrant adapters, interfaces.
3) Vertical slice: stage/validate/commit orchestration with idempotency + audit log.
4) Search: embedding interface + stub provider, Qdrant upsert/search.
5) Tests: unit (validation/idempotency), integration (stage/commit/search).
6) Seed script + README with exact local setup.

## Phase 0 Checklist
- [ ] docker-compose with postgres, neo4j, qdrant, api
- [ ] FastAPI app skeleton with /health
- [ ] .env and .env.example (no secrets)
- [ ] README with local setup steps
- [ ] Alembic migration base

## Phase 1 Checklist
- [ ] Stage endpoint with validation rules
- [ ] Commit endpoint idempotent + audit_log
- [ ] Postgres persistence for nodes + links
- [ ] Neo4j graph upsert for relationships
- [ ] Qdrant vector upsert + search
- [ ] Optional Notion mirror (env flag)
- [ ] Unit tests (validation, idempotency)
- [ ] Integration tests (stage/commit/search)
- [ ] Seed script for example node

