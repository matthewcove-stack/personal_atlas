# Personal Atlas (Canonical Memory) — Intent

## Goal
Build a “Personal Atlas” canonical long-term memory system with:
- **Truth store**: PostgreSQL (authoritative structured data)
- **Knowledge graph**: Neo4j (relationships/causality)
- **Semantic recall**: Qdrant (vector similarity search)
- **Human projection layer**: Notion (editable UI, synced from canonical stores)
- **Control plane**: API service + optional MCP server (tools for ChatGPT/Codex to read/write safely)

This system should support:
- Creating and updating “Atlas Nodes” (principles, evidence, confidence, last verified)
- Linking nodes to projects, SOPs, materials, tools, failure modes, and decisions
- Querying by exact filters (SQL/graph) and fuzzy semantic recall (Qdrant)
- A safe write workflow: stage → validate → commit (idempotent)

## Non-goals (for MVP)
- Full UI (beyond minimal API + Notion projection)
- Complex auth/OAuth (use local/dev auth first)
- Multi-user tenancy
- Cloud deployment polish (can come later)

## Key design principles
1) **Canonical truth is owned by us** (Postgres + Neo4j + Qdrant). Notion is a projection/editing surface, not the system of record.
2) **Writes are explicit and auditable** (stage/commit, idempotency keys, audit log).
3) **Safe automation boundary**: Tools that can write must be narrowly scoped (allowlisted resources, no arbitrary Notion writes).
4) **AI-native workflow**: docs and architecture first, incremental phases, tests, repeatable dev environment.

## MVP scope (Phase 0–1)
### Phase 0 (Scaffold + contracts)
- Repo scaffold with Docker Compose for:
  - postgres
  - neo4j
  - qdrant
  - api service (FastAPI)
- Define schemas:
  - Postgres tables for atlas_nodes, decisions, sops, projects, audit_log
  - Neo4j node labels + relationships (documented)
  - Qdrant collections + embedding strategy (documented; implement stub embeddings initially)
- API endpoints (FastAPI):
  - POST /atlas/nodes/stage
  - POST /atlas/nodes/commit
  - GET  /atlas/nodes/{id}
  - GET  /atlas/search?q=...
  - GET  /health
- Minimal Notion sync module (can be disabled): write Atlas nodes to a Notion database (configured by env vars).

### Phase 1 (Working vertical slice)
- End-to-end flow:
  - stage node -> validate -> commit
  - persist to Postgres
  - create/update graph links in Neo4j
  - upsert vector embedding into Qdrant (use a placeholder embedding provider interface with a local stub; later can plug in OpenAI embeddings)
  - (optional) mirror to Notion
- Add basic “linking” capability:
  - Link AtlasNode -> Project and AtlasNode -> Material/Tool
- Add tests:
  - unit tests for validation/idempotency
  - integration tests that spin up docker services and verify write/search
- Add CLI dev helper (Makefile or scripts):
  - bootstrap
  - migrate
  - run tests
  - seed example node(s)

## Tech stack
- Python 3.12+
- FastAPI + Pydantic
- SQLAlchemy or SQLModel + Alembic migrations
- Neo4j Python driver
- Qdrant client
- pytest
- Docker + docker-compose

## Operating constraints
- Default to local dev environment (Docker).
- No secrets in repo. Use .env (example provided).
- Every write must be idempotent via idempotency_key and an audit trail row.
- Prefer “read-only planning” first, then apply diffs.

## Deliverables
- Working `docker compose up` brings all services up
- `make test` (or equivalent) runs unit + integration tests
- Documented architecture and data model
- Example: commit an Atlas node and retrieve it via exact and semantic search

## Future phases (later)
- Proper auth (JWT/OAuth)
- MCP server that exposes safe tools: atlas_search, atlas_stage, atlas_commit
- Bidirectional Notion sync with conflict resolution
- Web UI
- Scheduling “re-verify” reminders
