# Architecture

## Overview
Personal Atlas is a local-first canonical memory system that stores authoritative data in Postgres, relationships in Neo4j, and semantic vectors in Qdrant. A FastAPI service exposes a gated write workflow (stage -> validate -> commit) and read/query endpoints. Notion mirroring is optional and disabled by default.

## Components
- API service (FastAPI)
  - HTTP endpoints for staging, committing, reading, and searching Atlas nodes.
  - Orchestrates validation, idempotency, persistence, graph updates, and vector upserts.
- Postgres (truth store)
  - Authoritative structured storage for Atlas nodes, links, and audit logs.
- Neo4j (knowledge graph)
  - Stores nodes and edges for relationships (projects, materials, tools).
- Qdrant (semantic recall)
  - Stores embeddings for Atlas nodes and supports top-k similarity search.
- Notion mirror (optional)
  - One-way projection of committed Atlas nodes to a Notion database.

## Clean Architecture Layout
- core/
  - domain models, validation rules, and interfaces (ports) for adapters.
- services/
  - application services for stage/commit/search flows and idempotency handling.
- adapters/
  - postgres, neo4j, qdrant, notion implementations of core interfaces.
- api/
  - FastAPI routers, request/response schemas, dependency wiring.

## Write Workflow
1) Stage: validate payload, store a staged record with idempotency_key, write audit log.
2) Commit: load staged record by idempotency_key, persist to Postgres, update Neo4j, upsert to Qdrant, optional Notion mirror, write audit log.
3) Idempotency: same idempotency_key returns the existing result without duplicates.

## Observability
- Every write produces an audit_log row with action, entity, idempotency_key, and status.

