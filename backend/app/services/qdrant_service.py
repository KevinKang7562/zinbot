from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.config import settings


class QdrantService:
    def __init__(self) -> None:
        self.client = AsyncQdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )
        self.collection = settings.qdrant_collection

    async def ensure_collection(self, vector_size: int) -> None:
        collections = await self.client.get_collections()
        names = {c.name for c in collections.collections}
        if self.collection in names:
            return
        await self.client.create_collection(
            collection_name=self.collection,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )

    async def upsert_chunks(
        self,
        chunks: list[str],
        vectors: list[list[float]],
        title: str,
        source: str,
        metadata: dict[str, Any],
        doc_type: str,
    ) -> int:
        if not chunks:
            return 0
        await self.ensure_collection(len(vectors[0]))

        now_iso = datetime.now(timezone.utc).isoformat()
        total_chunks = len(chunks)
        points = []
        for idx, (chunk, vector) in enumerate(zip(chunks, vectors)):
            payload = {
                "title": title,
                "text": chunk,
                "source": source,
                "metadata": metadata,
                "type": doc_type,
                "created_at": now_iso,
                "chunk_index": idx,
                "total_chunks": total_chunks,
            }
            points.append(PointStruct(id=str(uuid4()), vector=vector, payload=payload))

        await self.client.upsert(collection_name=self.collection, points=points, wait=True)
        return len(points)

    async def search(self, query_vector: list[float], threshold: float, limit: int = 5):
        try:
            return await self.client.search(
                collection_name=self.collection,
                query_vector=query_vector,
                score_threshold=threshold,
                limit=limit,
                with_payload=True,
            )
        except Exception:
            return []

    async def list_embeddings(self, limit: int = 200) -> list[dict[str, Any]]:
        try:
            points, _ = await self.client.scroll(
                collection_name=self.collection,
                limit=limit,
                with_payload=True,
            )
        except Exception:
            return []

        grouped: dict[tuple[str, str, str, int], dict[str, Any]] = {}
        for p in points:
            payload = p.payload or {}
            title = payload.get("title", "")
            source = payload.get("source", "")
            doc_type = payload.get("type", "")
            total_chunks = int(payload.get("total_chunks") or 0)
            key = (title, source, doc_type, total_chunks)

            if key not in grouped:
                grouped[key] = {
                    "id": str(p.id),
                    "title": title,
                    "source": source,
                    "doc_type": doc_type,
                    "total_chunks": total_chunks,
                    "created_at": payload.get("created_at"),
                    "metadata": payload.get("metadata", {}),
                    "chunk_count": 1,
                }
                continue

            row = grouped[key]
            row["chunk_count"] += 1
            current_created_at = row.get("created_at") or ""
            candidate_created_at = payload.get("created_at") or ""
            if candidate_created_at > current_created_at:
                row["id"] = str(p.id)
                row["created_at"] = candidate_created_at
                row["metadata"] = payload.get("metadata", {})

        rows: list[dict[str, Any]] = []
        for row in grouped.values():
            if row["total_chunks"] <= 0:
                row["total_chunks"] = row["chunk_count"]
            row.pop("chunk_count", None)
            rows.append(row)

        rows.sort(key=lambda item: item.get("created_at") or "", reverse=True)
        return rows


qdrant_service = QdrantService()
