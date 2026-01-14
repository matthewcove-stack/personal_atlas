from datetime import date

from pydantic import BaseModel, Field, field_validator


class AtlasNodeInput(BaseModel):
    domain: str = Field(..., min_length=1)
    subsystem: str = Field(..., min_length=1)
    principle: str = Field(..., min_length=1)
    full_knowledge: str = Field(..., min_length=1)
    evidence: str | None = None
    tools_materials: str | None = None
    confidence: int = Field(..., ge=1, le=5)
    last_verified: date
    idempotency_key: str = Field(..., min_length=1)

    @field_validator("domain", "subsystem", "principle", "full_knowledge", "idempotency_key")
    @classmethod
    def _strip_required(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("field must be non-empty")
        return v
