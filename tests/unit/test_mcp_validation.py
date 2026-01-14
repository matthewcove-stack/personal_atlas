import pytest
from pydantic import ValidationError

from app.mcp_server.schemas import AtlasNodeInput


def test_mcp_rejects_empty_principle() -> None:
    with pytest.raises(ValidationError):
        AtlasNodeInput(
            domain="domain",
            subsystem="subsystem",
            principle=" ",
            full_knowledge="knowledge",
            evidence=None,
            tools_materials=None,
            confidence=3,
            last_verified="2025-01-01",
            idempotency_key="key",
        )


def test_mcp_rejects_confidence_out_of_range() -> None:
    with pytest.raises(ValidationError):
        AtlasNodeInput(
            domain="domain",
            subsystem="subsystem",
            principle="principle",
            full_knowledge="knowledge",
            evidence=None,
            tools_materials=None,
            confidence=9,
            last_verified="2025-01-01",
            idempotency_key="key",
        )
