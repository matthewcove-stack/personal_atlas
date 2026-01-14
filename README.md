# Personal Atlas (Phase 0-1)

## Requirements
- Docker + Docker Compose
- Python 3.12+ (for local scripts/tests)

## Local Setup
1) Copy env file if needed:
   - `.env` already included for local dev
   - update `.env` if you want different credentials
2) Start services:
```bash
docker compose up -d
```
Windows (PowerShell):
```powershell
docker compose up -d
```
3) Run migrations:
```bash
alembic upgrade head
```
Windows (PowerShell):
```powershell
alembic upgrade head
```
4) API is available at: http://localhost:8000

## Run Tests
```bash
pytest
```
Windows (PowerShell):
```powershell
pytest
```

## Seed Example
```bash
python scripts/seed.py
```
Windows (PowerShell):
```powershell
python scripts\seed.py
```

## Phase 2: MCP Server
Run MCP server locally:
```bash
python -m app.mcp_server.main
```
Windows (PowerShell):
```powershell
python -m app.mcp_server.main
```

Run smoke test:
```bash
python scripts/mcp_smoke_test.py
```
Windows (PowerShell):
```powershell
python scripts\mcp_smoke_test.py
```

Expose MCP server via ngrok:
```bash
ngrok http 8765
```
Windows (PowerShell):
```powershell
ngrok http 8765
```

ChatGPT integration steps are in `CHATGPT_INTEGRATION.md`.

## Curl Examples
Stage:
```bash
curl -X POST http://localhost:8000/atlas/nodes/stage \
  -H "Content-Type: application/json" \
  -d '{
    "idempotency_key": "demo-1",
    "title": "MDF finishing & material choice",
    "principle": "Seal MDF edges before paint to avoid fuzzing.",
    "evidence": "Shellac reduces edge fuzz and absorbs less paint.",
    "confidence": 4,
    "last_verified": "2025-01-01",
    "links": [{"type":"material","value":"MDF"}]
  }'
```

Commit:
```bash
curl -X POST http://localhost:8000/atlas/nodes/commit \
  -H "Content-Type: application/json" \
  -d '{"idempotency_key":"demo-1"}'
```

Get:
```bash
curl http://localhost:8000/atlas/nodes/<id>
```

Search:
```bash
curl "http://localhost:8000/atlas/search?q=MDF&k=3"
```

## Makefile Targets
```bash
make up
make down
make api
make mcp
make test
make seed
```
Windows note: `make` isn't available by default. Use the direct commands above or the PowerShell scripts in `scripts\` for migrations/tests.

## Notion Mirror (Optional)
- Set `NOTION_ENABLED=true`, `NOTION_TOKEN`, and `NOTION_DATABASE_ID` in `.env`.
- The Notion database should have properties: `Title` (title), `Principle` (rich_text),
  `Confidence` (number), `LastVerified` (date), and `AtlasId` (rich_text).
