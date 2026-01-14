import time
import uuid

import pytest
import requests


BASE_URL = "http://localhost:8000"


def _health_ok() -> bool:
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=2)
        return resp.status_code == 200
    except requests.RequestException:
        return False


@pytest.mark.skipif(not _health_ok(), reason="API not available")
def test_stage_commit_search_flow() -> None:
    key = f"itest-{uuid.uuid4()}"
    payload = {
        "idempotency_key": key,
        "title": "MDF finishing & material choice",
        "principle": "Seal MDF edges before paint to avoid fuzzing.",
        "evidence": "Shop tests show reduced sanding and smoother finish.",
        "confidence": 4,
        "last_verified": "2025-01-01",
        "links": [{"type": "material", "value": "MDF"}],
    }
    stage = requests.post(f"{BASE_URL}/atlas/nodes/stage", json=payload, timeout=5)
    assert stage.status_code == 200
    node_id = stage.json()["id"]

    commit = requests.post(
        f"{BASE_URL}/atlas/nodes/commit",
        json={"idempotency_key": key},
        timeout=5,
    )
    assert commit.status_code == 200

    node = requests.get(f"{BASE_URL}/atlas/nodes/{node_id}", timeout=5)
    assert node.status_code == 200
    assert node.json()["id"] == node_id

    time.sleep(0.5)
    search = requests.get(f"{BASE_URL}/atlas/search", params={"q": "MDF", "k": 3}, timeout=5)
    assert search.status_code == 200
    results = search.json()["results"]
    assert any(r["id"] == node_id for r in results)
