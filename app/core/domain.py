from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True)
class AtlasLink:
    link_type: str
    link_value: str


@dataclass(frozen=True)
class AtlasNode:
    id: str
    title: str
    principle: str
    evidence: str | None
    confidence: int
    last_verified: date
    status: str
    idempotency_key: str
    created_at: datetime
    updated_at: datetime
