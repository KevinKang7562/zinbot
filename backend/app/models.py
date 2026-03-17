from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)


class ChatResponse(BaseModel):
    answer: str
    used_context: bool
    references: list[dict[str, Any]]


class TextEmbeddingRequest(BaseModel):
    title: str = Field(min_length=1)
    text: str = Field(min_length=1)
    source: str = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class EmbeddingRecord(BaseModel):
    id: str
    title: str
    source: str
    doc_type: str
    total_chunks: int
    created_at: datetime
    metadata: dict[str, Any]


class EmbeddingListResponse(BaseModel):
    items: list[EmbeddingRecord]
