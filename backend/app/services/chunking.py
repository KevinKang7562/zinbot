import re


SENTENCE_SPLIT_REGEX = re.compile(r"(?<=[\.\!\?\u3002\uFF01\uFF1F])\s+")


def split_sentences(text: str) -> list[str]:
    normalized = re.sub(r"\n{2,}", "\n", text).strip()
    if not normalized:
        return []
    parts = SENTENCE_SPLIT_REGEX.split(normalized)
    return [p.strip() for p in parts if p and p.strip()]


def semantic_chunk(
    text: str,
    max_chars: int = 800,
    min_chunk_chars: int = 180,
    overlap_sentences: int = 1,
) -> list[str]:
    sentences = split_sentences(text)
    if not sentences:
        return []

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for sent in sentences:
        sent_len = len(sent)
        if current and current_len + sent_len > max_chars and current_len >= min_chunk_chars:
            chunks.append(" ".join(current).strip())
            overlap = current[-overlap_sentences:] if overlap_sentences > 0 else []
            current = overlap + [sent]
            current_len = sum(len(s) for s in current)
            continue

        current.append(sent)
        current_len += sent_len

    if current:
        chunks.append(" ".join(current).strip())

    return [c for c in chunks if c]
