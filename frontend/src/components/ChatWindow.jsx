import { useState } from "react";
import { apiUrl } from "../api";

const URL_PATTERN = /(\*\*(?:https?:\/\/|www\.)[^\s*]+\*\*|(?:https?:\/\/|www\.)[^\s]+)/g;

async function postChat(message) {
  const res = await fetch(apiUrl("/api/chat"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(detail || "채팅 요청 실패");
  }
  return res.json();
}

function normalizeReferenceText(text) {
  if (!text) return "근거 본문 없음";
  return text.replace(/\s*\n+\s*/g, " ").replace(/\s{2,}/g, " ").trim();
}

function toReferenceParagraphs(text) {
  const fallback = ["근거 본문 없음"];
  if (!text) return fallback;

  const normalizedLineBreaks = text.replace(/\r\n/g, "\n").trim();
  if (!normalizedLineBreaks) return fallback;

  const explicitParagraphs = normalizedLineBreaks
    .split(/\n{2,}/)
    .map((paragraph) => paragraph.replace(/\s*\n\s*/g, " ").replace(/\s{2,}/g, " ").trim())
    .filter(Boolean);

  if (explicitParagraphs.length > 1) {
    return explicitParagraphs;
  }

  const compact = normalizeReferenceText(normalizedLineBreaks);
  if (!compact) return fallback;

  const sentenceChunks = compact
    .replace(/([.!?]["']?|니다|습니다|한다|했다|됩니다|하세요|하세요\.?|이에요|예요|어요|아요|죠|요|다)\s+/g, "$1\n")
    .split("\n")
    .map((chunk) => chunk.trim())
    .filter(Boolean);

  if (sentenceChunks.length <= 2) {
    return [compact];
  }

  const paragraphs = [];
  let current = "";

  sentenceChunks.forEach((chunk) => {
    const next = current ? `${current} ${chunk}` : chunk;
    if (next.length > 140 && current) {
      paragraphs.push(current);
      current = chunk;
      return;
    }
    current = next;
  });

  if (current) {
    paragraphs.push(current);
  }

  return paragraphs.length > 0 ? paragraphs : [compact];
}

function splitUrlSuffix(url) {
  const match = url.match(/[),.!?]+$/);
  if (!match) {
    return { href: url, suffix: "" };
  }

  return {
    href: url.slice(0, -match[0].length),
    suffix: match[0],
  };
}

function unwrapDecoratedUrl(text) {
  if (text.startsWith("**") && text.endsWith("**")) {
    return text.slice(2, -2);
  }
  return text;
}

function toHref(url) {
  if (url.startsWith("www.")) {
    return `https://${url}`;
  }
  return url;
}

function renderTextWithLinks(text) {
  if (!text) return null;

  return text.split(URL_PATTERN).map((part, idx) => {
    if (!part) {
      return null;
    }

    const rawUrl = unwrapDecoratedUrl(part);

    if (!rawUrl.match(/^(https?:\/\/|www\.)/)) {
      return part;
    }

    const { href, suffix } = splitUrlSuffix(rawUrl);
    const linkHref = toHref(href);
    return (
      <span key={`${href}-${idx}`}>
        <a className="inline-link" href={linkHref} target="_blank" rel="noreferrer">
          {href}
        </a>
        {suffix}
      </span>
    );
  });
}

export default function ChatWindow() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: "안녕하세요. zinbot입니다. 무엇을 도와드릴까요?",
      references: [],
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const send = async () => {
    const text = input.trim();
    if (!text || loading) return;

    setMessages((prev) => [...prev, { role: "user", text }]);
    setInput("");
    setLoading(true);

    try {
      const data = await postChat(text);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: data.answer,
          references: data.used_context ? data.references || [] : [],
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: `오류가 발생했습니다: ${err.message}`, references: [] },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && e.ctrlKey) {
      e.preventDefault();
      send();
    }
  };

  return (
    <section className="chat-panel">
      <div className="chat-log">
        {messages.map((m, idx) => (
          <div key={idx} className={`bubble ${m.role}`}>
            <div className="bubble-text">{renderTextWithLinks(m.text)}</div>
            {m.references?.length > 0 && (
              <div className="reference-section">
                <strong className="reference-title">근거</strong>
                <div className="reference-list">
                  {m.references.map((ref, refIdx) => (
                    <div key={refIdx} className="reference-item">
                      <div className="reference-head">
                        <span>{ref.title || "무제"}</span>
                        <span>{typeof ref.score === "number" ? ref.score.toFixed(3) : ref.score}</span>
                      </div>
                      <div className="reference-source">{ref.source || "출처없음"}</div>
                      <div className="reference-text">
                        {toReferenceParagraphs(ref.text).map((paragraph, paragraphIdx) => (
                          <p key={paragraphIdx} className="reference-paragraph">
                            {paragraph}
                          </p>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="composer">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={"메시지를 입력하세요.\nEnter: 줄바꿈, Ctrl+Enter: 전송"}
          rows={4}
        />
        <button type="button" onClick={send} disabled={loading}>
          {loading ? "전송중..." : "보내기"}
        </button>
      </div>
    </section>
  );
}
