from fastapi import APIRouter, HTTPException

from app.config import settings
from app.models import ChatRequest, ChatResponse
from app.services.llm_client import llm_client
from app.services.qdrant_service import qdrant_service

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def ask_chatbot(req: ChatRequest) -> ChatResponse:
    try:
        query_vector = await llm_client.embed(req.message, is_query=True)
        threshold = max(settings.score_threshold, 0.80)
        results = await qdrant_service.search(
            query_vector=query_vector,
            threshold=threshold,
            limit=5,
        )

        references = []
        if results:
            context_lines = []
            for hit in results:
                payload = hit.payload or {}
                title = payload.get("title", "")
                text = payload.get("text", "")
                source = payload.get("source", "")
                references.append(
                    {
                        "score": hit.score,
                        "title": title,
                        "source": source,
                        "text": text,
                    }
                )
                context_lines.append(f"[제목] {title}\n[출처] {source}\n[내용] {text}")

            system_prompt = (
                "당신은 사내 지식 기반 챗봇입니다. 주어진 근거만 사용해 답변을 정제하고, "
                "불확실하면 모른다고 말하세요."
            )
            user_prompt = (
                f"질문: {req.message}\n\n"
                f"근거 자료:\n{'\n\n'.join(context_lines)}\n\n"
                "근거를 바탕으로 간결하고 정확하게 한국어로 답변하세요."
            )
            answer = await llm_client.chat(
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
            )
            return ChatResponse(answer=answer, used_context=True, references=references)

        answer = await llm_client.chat(
            [
                {
                    "role": "system",
                    "content": "당신은 친절하고 정확한 한국어 비서입니다. 모르면 추측하지 마세요.",
                },
                {"role": "user", "content": req.message},
            ],
            temperature=0.2,
        )
        return ChatResponse(answer=answer, used_context=False, references=[])
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
