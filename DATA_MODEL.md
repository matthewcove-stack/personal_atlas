# Data Model

## Postgres (authoritative)
Tables are designed for idempotent writes and auditability.

### atlas_nodes
- id (uuid, pk)
- title (text, not null)
- principle (text, not null)
- evidence (text, nullable)
- confidence (int, not null, 1..5)
- last_verified (date, not null)
- status (text, not null) ["staged","committed"]
- idempotency_key (text, not null, unique for staged/commit scope)
- created_at (timestamptz, not null)
- updated_at (timestamptz, not null)

### atlas_links
- id (uuid, pk)
- atlas_node_id (uuid, fk -> atlas_nodes.id)
- link_type (text, not null) ["project","material","tool"]
- link_value (text, not null)
- created_at (timestamptz, not null)
- unique (atlas_node_id, link_type, link_value)

### audit_log
- id (uuid, pk)
- action (text, not null) ["stage","commit","graph_update","vector_upsert","notion_mirror"]
- entity_type (text, not null) ["atlas_node","atlas_link"]
- entity_id (uuid, nullable)
- idempotency_key (text, not null)
- status (text, not null) ["success","noop","error"]
- message (text, nullable)
- created_at (timestamptz, not null)

## Neo4j (relationships)
### Node Labels
- AtlasNode {id, title, principle, confidence, last_verified}
- Project {name}
- Material {name}
- Tool {name}

### Relationships
- (AtlasNode)-[:RELATES_TO]->(Project)
- (AtlasNode)-[:RELATES_TO]->(Material)
- (AtlasNode)-[:RELATES_TO]->(Tool)

## Qdrant (semantic vectors)
### Collection: atlas_nodes
- vector size: set by embedding provider (stub initially)
- payload:
  - id (uuid)
  - title
  - principle
  - confidence
  - last_verified

