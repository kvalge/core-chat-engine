import { useState } from "react";
import Chat from "./components/Chat";
import Sidebar from "./components/Sidebar";
import BackendConfig from "./components/BackendConfig";

type Page = "chat" | "settings";

function App() {
  const [currentPage, setCurrentPage] = useState<Page>("chat");
  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(null);

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      <Sidebar
        onNavigate={setCurrentPage}
        currentPage={currentPage}
        selectedProjectId={selectedProjectId}
        onSelectProject={setSelectedProjectId}
      />
      <main style={{ flex: 1, display: "flex", flexDirection: "column" }}>
        {currentPage === "chat" ? (
          <Chat projectId={selectedProjectId} />
        ) : (
          <BackendConfig />
        )}
      </main>
    </div>
  );
}

export default App;
