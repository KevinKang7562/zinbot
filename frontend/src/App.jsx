import { useMemo, useState } from "react";
import AdminPanel from "./components/AdminPanel";
import ChatWindow from "./components/ChatWindow";
import zinbotLogo from "./assets/images/zinbot_logo.png";

function App() {
  const [isAdminOpen, setIsAdminOpen] = useState(false);
  const [refreshToken, setRefreshToken] = useState(0);

  const subtitle = useMemo(
    () => "사내 지식 기반 챗봇 · Qdrant + multilingual-e5 + Gemma",
    []
  );

  return (
    <div className="app-shell">
      <div className="ambient-bg" />
      <header className="topbar">
        <div className="topbar-brand">
          <img className="topbar-logo" src={zinbotLogo} alt="zinbot" />
          <p>{subtitle}</p>
        </div>
        <button
          className="admin-trigger"
          onClick={() => setIsAdminOpen((v) => !v)}
          type="button"
        >
          관리자메뉴
        </button>
      </header>

      <main className="content">
        <ChatWindow />
      </main>

      <AdminPanel
        open={isAdminOpen}
        onClose={() => setIsAdminOpen(false)}
        onEmbedded={() => setRefreshToken((v) => v + 1)}
        refreshToken={refreshToken}
      />
    </div>
  );
}

export default App;
