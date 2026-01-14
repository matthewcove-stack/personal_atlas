# ChatGPT Integration (Phase 2)

This doc explains how to run the MCP server locally, expose it via HTTPS, and connect it in ChatGPT Developer Mode.

## 1) Start services (API + MCP in Docker)
```bash
docker compose up -d
```
Windows (PowerShell):
```powershell
docker compose up -d
```

## 2) Run migrations (inside API container)
```bash
docker compose exec -T -e PYTHONPATH=/app api alembic upgrade head
```
Windows (PowerShell):
```powershell
docker compose exec -T -e PYTHONPATH=/app api alembic upgrade head
```

## 3) Expose MCP via HTTPS (ngrok)
```bash
ngrok config add-authtoken $env:NGROK_AUTHTOKEN
ngrok http 8765
```
Windows note: the `$env:` prefix is PowerShell-specific. In CMD use:
```cmd
ngrok config add-authtoken %NGROK_AUTHTOKEN%
```
Copy the HTTPS URL printed by ngrok, for example:
```
https://your-subdomain.ngrok-free.app
```

## 4) Connect in ChatGPT Developer Mode
1) Open ChatGPT Desktop/Web.
2) Enable Developer Mode.
3) Add a new MCP server and paste the HTTPS URL from ngrok, ending with `/sse`.

## 5) Test commands in ChatGPT
Examples:
- "search MDF"
- "stage node" with the required fields
- "commit node"

Example flow (search -> stage -> commit):
1) search MDF
2) stage node with:
   - domain: Woodworking
   - subsystem: Materials
   - principle: Seal MDF edges before paint
   - full_knowledge: Seal edges to avoid fuzzing
   - evidence: Shop tests show smoother finish
   - tools_materials: MDF, shellac
   - confidence: 4
   - last_verified: 2025-01-01
   - idempotency_key: any unique string
3) commit node with staged_id from step 2

## Notes
- The MCP server runs in Docker and connects to Postgres/Neo4j/Qdrant using `.env`.
- MCP SSE endpoint: `http://localhost:8765/sse` (use the ngrok URL + `/sse`).
