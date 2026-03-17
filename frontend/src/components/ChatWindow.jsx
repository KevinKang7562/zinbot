import { useState } from "react";

async function postChat(message) {
  const res = await fetch("/api/chat", {
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
            <div className="bubble-text">{m.text}</div>
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
                      <div className="reference-text">{normalizeReferenceText(ref.text)}</div>
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
