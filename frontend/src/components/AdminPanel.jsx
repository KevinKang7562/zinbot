import { useEffect, useState } from "react";

const TABS = {
  TEXT: "텍스트 직접 임베딩",
  FILE: "파일 임베딩",
  LIST: "임베딩 리스트",
};

async function loadEmbeddingList() {
  const res = await fetch("/api/admin/embeddings");
  if (!res.ok) throw new Error("임베딩 리스트 조회 실패");
  return res.json();
}

export default function AdminPanel({ open, onClose, onEmbedded, refreshToken }) {
  const [tab, setTab] = useState(TABS.TEXT);
  const [status, setStatus] = useState("");
  const [items, setItems] = useState([]);
  const [isUploadingFile, setIsUploadingFile] = useState(false);

  const [textForm, setTextForm] = useState({
    title: "",
    text: "",
    source: "",
    metadata: "{}",
  });

  const [fileForm, setFileForm] = useState({
    title: "",
    source: "",
    metadata: "{}",
    file: null,
  });

  useEffect(() => {
    if (tab === TABS.LIST && open) {
      loadEmbeddingList()
        .then((data) => setItems(data.items || []))
        .catch((err) => setStatus(err.message));
    }
  }, [tab, open, refreshToken]);

  const submitTextEmbedding = async () => {
    setStatus("");
    try {
      const metadata = JSON.parse(textForm.metadata || "{}");
      const res = await fetch("/api/admin/embed/text", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: textForm.title,
          text: textForm.text,
          source: textForm.source,
          metadata,
        }),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setStatus(`텍스트 임베딩 완료: ${data.inserted}건 저장`);
      onEmbedded();
    } catch (err) {
      setStatus(`오류: ${err.message}`);
    }
  };

  const submitFileEmbedding = async () => {
    if (!fileForm.file || isUploadingFile) {
      setStatus("파일을 먼저 선택하세요.");
      return;
    }
    setStatus("파일 업로드 및 임베딩 진행 중입니다...");
    setIsUploadingFile(true);
    try {
      JSON.parse(fileForm.metadata || "{}");
      const formData = new FormData();
      formData.append("title", fileForm.title);
      formData.append("source", fileForm.source);
      formData.append("metadata_json", fileForm.metadata || "{}");
      formData.append("file", fileForm.file);

      const res = await fetch("/api/admin/embed/file", {
        method: "POST",
        body: formData,
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setStatus(`파일 임베딩 완료: ${data.inserted}건 저장`);
      onEmbedded();
    } catch (err) {
      setStatus(`오류: ${err.message}`);
    } finally {
      setIsUploadingFile(false);
    }
  };

  return (
    <>
      <div className={`drawer-mask ${open ? "show" : ""}`} onClick={onClose} />
      <aside className={`admin-drawer ${open ? "open" : ""}`}>
        <h2>관리자메뉴</h2>
        <nav className="menu-tabs">
          {Object.values(TABS).map((name) => (
            <button
              type="button"
              key={name}
              className={tab === name ? "active" : ""}
              onClick={() => setTab(name)}
            >
              {name}
            </button>
          ))}
        </nav>

        {tab === TABS.TEXT && (
          <section className="admin-form">
            <label>제목</label>
            <input
              value={textForm.title}
              onChange={(e) => setTextForm({ ...textForm, title: e.target.value })}
            />
            <label>내용</label>
            <textarea
              rows={6}
              value={textForm.text}
              onChange={(e) => setTextForm({ ...textForm, text: e.target.value })}
            />
            <label>출처</label>
            <input
              value={textForm.source}
              onChange={(e) => setTextForm({ ...textForm, source: e.target.value })}
            />
            <label>추가 메타데이터(JSON)</label>
            <textarea
              rows={4}
              value={textForm.metadata}
              onChange={(e) => setTextForm({ ...textForm, metadata: e.target.value })}
            />
            <button type="button" onClick={submitTextEmbedding}>
              텍스트 임베딩
            </button>
          </section>
        )}

        {tab === TABS.FILE && (
          <section className="admin-form">
            <label>제목</label>
            <input
              value={fileForm.title}
              onChange={(e) => setFileForm({ ...fileForm, title: e.target.value })}
            />
            <label>출처</label>
            <input
              value={fileForm.source}
              onChange={(e) => setFileForm({ ...fileForm, source: e.target.value })}
            />
            <label>추가 메타데이터(JSON)</label>
            <textarea
              rows={4}
              value={fileForm.metadata}
              onChange={(e) => setFileForm({ ...fileForm, metadata: e.target.value })}
            />
            <label>파일선택</label>
            <input
              type="file"
              accept=".txt,.md,.pdf,.pptx,.png,.jpg,.jpeg,.bmp,.tiff"
              disabled={isUploadingFile}
              onChange={(e) =>
                setFileForm({ ...fileForm, file: e.target.files?.[0] || null })
              }
            />
            <button type="button" onClick={submitFileEmbedding} disabled={isUploadingFile}>
              {isUploadingFile ? "업로드중..." : "파일업로드"}
            </button>
          </section>
        )}

        {tab === TABS.LIST && (
          <section className="admin-table-wrap">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>제목</th>
                  <th>출처</th>
                  <th>유형</th>
                  <th>청킹수</th>
                  <th>생성일</th>
                  <th>추가 메타데이터</th>
                </tr>
              </thead>
              <tbody>
                {items.map((item) => (
                  <tr key={item.id}>
                    <td>{item.title}</td>
                    <td>{item.source}</td>
                    <td>{item.doc_type}</td>
                    <td>{item.total_chunks}</td>
                    <td>{new Date(item.created_at).toLocaleString()}</td>
                    <td>{JSON.stringify(item.metadata || {})}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        )}

        {status && <p className="status-line">{status}</p>}
      </aside>
    </>
  );
}
