# API Contract

Base URL: http://localhost:8000

## GET /health
Response 200
```json
{"status":"ok"}
```

## POST /atlas/nodes/stage
Stage an Atlas node for commit.

Request
```json
{
  "idempotency_key": "string",
  "title": "string",
  "principle": "string",
  "evidence": "string|null",
  "confidence": 1,
  "last_verified": "YYYY-MM-DD",
  "links": [
    {"type":"project","value":"string"},
    {"type":"material","value":"string"},
    {"type":"tool","value":"string"}
  ]
}
```

Response 200
```json
{
  "id": "uuid",
  "status": "staged"
}
```

## POST /atlas/nodes/commit
Commit a staged node by idempotency_key.

Request
```json
{
  "idempotency_key": "string"
}
```

Response 200
```json
{
  "id": "uuid",
  "status": "committed"
}
```

## GET /atlas/nodes/{id}
Fetch a committed node.

Response 200
```json
{
  "id": "uuid",
  "title": "string",
  "principle": "string",
  "evidence": "string|null",
  "confidence": 1,
  "last_verified": "YYYY-MM-DD",
  "links": [
    {"type":"project","value":"string"}
  ]
}
```

## GET /atlas/search?q=...&k=5
Semantic search across committed nodes.

Response 200
```json
{
  "results": [
    {
      "id": "uuid",
      "score": 0.0,
      "title": "string",
      "principle": "string"
    }
  ]
}
```

