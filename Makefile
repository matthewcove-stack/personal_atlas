up:
	docker compose up -d

down:
	docker compose down

api:
	uvicorn app.main:app --host 0.0.0.0 --port 8000

mcp:
	python -m app.mcp_server.main

test:
	pytest

seed:
	python scripts/seed.py
