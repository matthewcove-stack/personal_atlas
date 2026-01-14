from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class LinkPayload(BaseModel):
    type: Literal["project", "material", "tool"]
    value: str = Field(..., min_length=1)

    @field_validator("value")
    @classmethod
    def _strip_value(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("link value must be non-empty")
        return v


class StageRequest(BaseModel):
    idempotency_key: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    principle: str = Field(..., min_length=1)
    evidence: str | None = None
    confidence: int = Field(..., ge=1, le=5)
    last_verified: date
    links: list[LinkPayload] = []

    @field_validator("principle")
    @classmethod
    def _strip_principle(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("principle must be non-empty")
        return v


class StageResponse(BaseModel):
    id: str
    status: str


class CommitRequest(BaseModel):
    idempotency_key: str = Field(..., min_length=1)


class CommitResponse(BaseModel):
    id: str
    status: str


class NodeResponse(BaseModel):
    id: str
    title: str
    principle: str
    evidence: str | None
    confidence: int
    last_verified: date
    links: list[LinkPayload]


class SearchResponse(BaseModel):
    results: list[dict]
