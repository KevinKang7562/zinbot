from typing import Any

import httpx
import numpy as np

from app.config import settings
from app.services.text_normalizer import normalize_text


class LLMClient:
    def __init__(self) -> None:
        self.base_url = settings.llm_api_base.rstrip("/")
        self.chat_api_url = settings.llm_chat_api_url
        self.embedding_api_url = settings.embedding_api_url

    def _coerce_embedding_vector(self, data: Any) -> list[float]:
        if not isinstance(data, list) or not data:
            raise ValueError("임베딩 응답 형식이 올바르지 않습니다.")

        if isinstance(data[0], (int, float)):
            return [float(v) for v in data]

        # Some HF feature-extraction models return token-level vectors.
        if isinstance(data[0], list):
            matrix = np.asarray(data, dtype=float)
            if matrix.ndim == 2:
                return matrix.mean(axis=0).tolist()

        raise ValueError("지원하지 않는 임베딩 응답 형식입니다.")

    async def embed(self, text: str, is_query: bool = False) -> list[float]:
        prefix = "query: " if is_query else "passage: "
        normalized_text = normalize_text(text)
        payload: dict[str, Any] = {
            "inputs": f"{prefix}{normalized_text}",
            "normalize": True,
        }
        headers = {"Authorization": f"Bearer {settings.embedding_api_key}"}
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                self.embedding_api_url,
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
        return self._coerce_embedding_vector(data)

    async def chat(self, messages: list[dict[str, str]], temperature: float = 0.2) -> str:
        payload: dict[str, Any] = {
            "model": settings.llm_model,
            "messages": messages,
            "temperature": temperature,
        }
        headers = {"Authorization": f"Bearer {settings.llm_api_key}"}
        async with httpx.AsyncClient(timeout=90) as client:
            response = await client.post(self.chat_api_url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
        return data["choices"][0]["message"]["content"].strip()


llm_client = LLMClient()
