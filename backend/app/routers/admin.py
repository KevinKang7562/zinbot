import json
from datetime import datetime
from typing import Any

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.models import EmbeddingListResponse, EmbeddingRecord, TextEmbeddingRequest
from app.services.chunking import semantic_chunk
from app.services.file_extract import ALLOWED_EXTENSIONS, extract_text_from_file
from app.services.llm_client import llm_client
from app.services.qdrant_service import qdrant_service
from app.services.text_normalizer import normalize_text

router = APIRouter(prefix="/api/admin", tags=["admin"])


def _parse_metadata(metadata_json: str | None) -> dict[str, Any]:
    if not metadata_json:
        return {}
    try:
        data = json.loads(metadata_json)
        if not isinstance(data, dict):
            raise ValueError("metadata must be a JSON object")
        return data
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"metadata JSON 파싱 실패: {exc}") from exc


async def _embed_chunks(chunks: list[str]) -> list[list[float]]:
    vectors: list[list[float]] = []
    for chunk in chunks:
        vectors.append(await llm_client.embed(chunk, is_query=False))
    return vectors


@router.post("/embed/text")
async def embed_text(req: TextEmbeddingRequest):
    normalized_text = normalize_text(req.text)
    chunks = semantic_chunk(normalized_text)
    if not chunks:
        raise HTTPException(status_code=400, detail="텍스트에서 임베딩할 내용을 찾지 못했습니다.")

    vectors = await _embed_chunks(chunks)
    inserted = await qdrant_service.upsert_chunks(
        chunks=chunks,
        vectors=vectors,
        title=req.title,
        source=req.source,
        metadata=req.metadata,
        doc_type="text",
    )
    return {"inserted": inserted, "chunks": len(chunks)}


@router.post("/embed/file")
async def embed_file(
    title: str = Form(...),
    source: str = Form(...),
    metadata_json: str = Form(default="{}"),
    file: UploadFile = File(...),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="파일명이 없습니다.")

    ext = "." + file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise HTTPException(status_code=400, detail=f"허용 확장자: {allowed}")

    metadata = _parse_metadata(metadata_json)
    raw = await file.read()
    text = extract_text_from_file(file.filename, raw)
    if not text:
        raise HTTPException(status_code=400, detail="파일에서 텍스트를 추출하지 못했습니다.")

    chunks = semantic_chunk(text)
    if not chunks:
        raise HTTPException(status_code=400, detail="추출 텍스트를 청킹하지 못했습니다.")

    vectors = await _embed_chunks(chunks)
    inserted = await qdrant_service.upsert_chunks(
        chunks=chunks,
        vectors=vectors,
        title=title,
        source=source,
        metadata=metadata,
        doc_type=ext.lstrip("."),
    )
    return {"inserted": inserted, "chunks": len(chunks), "filename": file.filename}


@router.get("/embeddings", response_model=EmbeddingListResponse)
async def list_embeddings():
    rows = await qdrant_service.list_embeddings(limit=200)
    items: list[EmbeddingRecord] = []
    for row in rows:
        created = row.get("created_at")
        try:
            created_at = datetime.fromisoformat(created.replace("Z", "+00:00")) if created else datetime.now()
        except Exception:
            created_at = datetime.now()
        items.append(
            EmbeddingRecord(
                id=row["id"],
                title=row["title"],
                source=row["source"],
                doc_type=row["doc_type"],
                total_chunks=row.get("total_chunks", 0),
                created_at=created_at,
                metadata=row["metadata"],
            )
        )
    return EmbeddingListResponse(items=items)
