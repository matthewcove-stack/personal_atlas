import pytest
from pydantic import ValidationError

from app.api.schemas import StageRequest


def test_stage_request_rejects_empty_principle() -> None:
    with pytest.raises(ValidationError):
        StageRequest(
            idempotency_key="k1",
            title="title",
            principle="  ",
            evidence=None,
            confidence=3,
            last_verified="2025-01-01",
            links=[],
        )


def test_stage_request_rejects_confidence_out_of_range() -> None:
    with pytest.raises(ValidationError):
        StageRequest(
            idempotency_key="k2",
            title="title",
            principle="principle",
            evidence=None,
            confidence=6,
            last_verified="2025-01-01",
            links=[],
        )
