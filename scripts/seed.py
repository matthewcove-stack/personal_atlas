import os
import uuid

import requests


BASE_URL = os.getenv("ATLAS_API_URL", "http://localhost:8000")


def main() -> None:
    key = f"seed-{uuid.uuid4()}"
    payload = {
        "idempotency_key": key,
        "title": "MDF finishing & material choice",
        "principle": "Seal MDF edges before paint to avoid fuzzing.",
        "evidence": "Shellac or sanding sealer reduces edge fuzz and absorbs less paint.",
        "confidence": 4,
        "last_verified": "2025-01-01",
        "links": [{"type": "material", "value": "MDF"}],
    }
    stage = requests.post(f"{BASE_URL}/atlas/nodes/stage", json=payload, timeout=5)
    stage.raise_for_status()
    commit = requests.post(
        f"{BASE_URL}/atlas/nodes/commit",
        json={"idempotency_key": key},
        timeout=5,
    )
    commit.raise_for_status()
    print(f"Seeded node {commit.json()['id']}")


if __name__ == "__main__":
    main()
