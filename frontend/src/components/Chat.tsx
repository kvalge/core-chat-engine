import { useState, useRef, useEffect, useCallback } from "react";
import {
  streamingChatCompletion,
  ChatMessage,
  listConversations,
  createConversation,
  getConversationDetail,
  appendMessage,
  getProject,
  deleteConversation,
  newChatTitle,
  OLLAMA_LOCAL_MODELS,
  type Conversation,
} from "../services/api";

interface UiMessage {
  id: number;
  role: "user" | "assistant";
  content: string;
}

function mapRowsToUi(
  rows: { id: number; role: string; content: string }[]
): UiMessage[] {
  return rows
    .filter((m) => m.role === "user" || m.role === "assistant")
    .map((m) => ({
      id: m.id,
      role: m.role as "user" | "assistant",
      content: m.content,
    }));
}

interface ChatProps {
  projectId: number | null;
}

export default function Chat({ projectId }: ChatProps) {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<number | null>(
    null
  );
  const [messages, setMessages] = useState<UiMessage[]>([]);
  const [systemPrompt, setSystemPrompt] = useState("");
  const [model, setModel] = useState<string>("llama3.2");
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [booting, setBooting] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const loadMessages = useCallback(async (conversationId: number) => {
    const { messages: rows } = await getConversationDetail(conversationId);
    setMessages(mapRowsToUi(rows));
  }, []);

  useEffect(() => {
    if (projectId == null) {
      setConversations([]);
      setActiveConversationId(null);
      setMessages([]);
      setSystemPrompt("");
      return;
    }

    let cancelled = false;
    setBooting(true);

    (async () => {
      try {
        const proj = await getProject(projectId);
        if (cancelled) return;
        setSystemPrompt(proj.system_prompt || "");
        const dm = proj.default_model;
        setModel(
          (OLLAMA_LOCAL_MODELS as readonly string[]).includes(dm) ? dm : "llama3.2"
        );

        let convs = await listConversations(projectId);
        if (cancelled) return;
        if (convs.length === 0) {
          const c = await createConversation(projectId, newChatTitle());
          if (cancelled) return;
          convs = [c];
        }
        setConversations(convs);
        const firstId = convs[0].id;
        setActiveConversationId(firstId);
        await loadMessages(firstId);
      } finally {
        if (!cancelled) setBooting(false);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [projectId, loadMessages]);

  const startNewChat = async () => {
    if (!projectId || loading) return;
    setLoading(true);
    try {
      const c = await createConversation(projectId, newChatTitle());
      setConversations((prev) => [c, ...prev]);
      setActiveConversationId(c.id);
      setMessages([]);
    } catch (e) {
      console.error(e);
      alert(e instanceof Error ? e.message : "Could not start a new chat");
    } finally {
      setLoading(false);
    }
  };

  const deleteCurrentChat = async () => {
    if (!projectId || !activeConversationId || loading || booting) return;
    if (
      !confirm(
        "Delete this chat and all of its messages? This cannot be undone."
      )
    )
      return;
    setLoading(true);
    try {
      const idToRemove = activeConversationId;
      await deleteConversation(idToRemove);
      let next = await listConversations(projectId);
      if (next.length === 0) {
        const c = await createConversation(projectId, newChatTitle());
        next = [c];
      }
      setConversations(next);
      const pick = next[0].id;
      setActiveConversationId(pick);
      await loadMessages(pick);
    } catch (e) {
      console.error(e);
      alert(e instanceof Error ? e.message : "Could not delete chat");
    } finally {
      setLoading(false);
    }
  };

  const onPickConversation = async (id: number) => {
    if (id === activeConversationId || loading) return;
    setActiveConversationId(id);
    setBooting(true);
    try {
      await loadMessages(id);
    } catch (e) {
      console.error(e);
      alert(e instanceof Error ? e.message : "Could not load chat");
    } finally {
      setBooting(false);
    }
  };

  const sendMessage = async () => {
    if (
      !projectId ||
      !activeConversationId ||
      !input.trim() ||
      loading ||
      booting
    )
      return;

    const userText = input.trim();
    setInput("");
    setLoading(true);

    const assistantLocalId = -(Date.now());

    try {
      await appendMessage(activeConversationId, {
        role: "user",
        content: userText,
      });
      const { messages: rows } = await getConversationDetail(activeConversationId);
      const thread = mapRowsToUi(rows);

      const llmMessages: ChatMessage[] = [];
      if (systemPrompt.trim()) {
        llmMessages.push({ role: "system", content: systemPrompt });
      }
      for (const m of thread) {
        llmMessages.push({ role: m.role, content: m.content });
      }

      setMessages([...thread, { id: assistantLocalId, role: "assistant", content: "" }]);

      let fullContent = "";
      for await (const chunk of streamingChatCompletion({
        model,
        messages: llmMessages,
      })) {
        fullContent += chunk;
        setMessages([
          ...thread,
          { id: assistantLocalId, role: "assistant", content: fullContent },
        ]);
      }

      if (!fullContent.trim()) {
        setMessages([
          ...thread,
          {
            id: assistantLocalId,
            role: "assistant",
            content: "Sorry, I didn't get a response.",
          },
        ]);
      } else {
        await appendMessage(activeConversationId, {
          role: "assistant",
          content: fullContent,
        });
        const { messages: finalRows } = await getConversationDetail(
          activeConversationId
        );
        setMessages(mapRowsToUi(finalRows));
      }

      setConversations(await listConversations(projectId));
    } catch (error) {
      console.error("Error:", error);
      try {
        await loadMessages(activeConversationId);
      } catch {
        setMessages((prev) => {
          const withoutGhost = prev.filter((m) => m.id !== assistantLocalId);
          return [
            ...withoutGhost,
            {
              id: Date.now(),
              role: "assistant",
              content:
                error instanceof Error
                  ? `Error: ${error.message}`
                  : "Error: Could not complete chat.",
            },
          ];
        });
      }
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void sendMessage();
    }
  };

  if (projectId == null) {
    return (
      <div style={{ padding: "2rem", color: "#666" }}>
        Select a project in the sidebar, or create one with <strong>+ New Project</strong>.
      </div>
    );
  }

  return (
    <div style={{ flex: 1, display: "flex", flexDirection: "column", padding: "1rem" }}>
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: "0.75rem",
          alignItems: "center",
          marginBottom: "1rem",
          paddingBottom: "0.75rem",
          borderBottom: "1px solid #e5e7eb",
        }}
      >
        <label style={{ fontSize: "0.875rem" }}>
          Model{" "}
          <select
            value={model}
            onChange={(e) => setModel(e.target.value)}
            disabled={loading || booting}
            style={{ marginLeft: "0.25rem", padding: "0.35rem 0.5rem" }}
          >
            {OLLAMA_LOCAL_MODELS.map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
        </label>
        <label style={{ fontSize: "0.875rem" }}>
          Previous chats{" "}
          <select
            value={activeConversationId ?? ""}
            onChange={(e) => void onPickConversation(Number(e.target.value))}
            disabled={loading || booting || conversations.length === 0}
            style={{ marginLeft: "0.25rem", padding: "0.35rem 0.5rem", minWidth: "10rem" }}
          >
            {conversations.map((c) => (
              <option key={c.id} value={c.id}>
                {c.title}
              </option>
            ))}
          </select>
        </label>
        <button
          type="button"
          onClick={() => void startNewChat()}
          disabled={loading || booting}
          style={{
            padding: "0.4rem 0.75rem",
            backgroundColor: "#3b82f6",
            color: "white",
            border: "none",
            borderRadius: "0.375rem",
            cursor: loading || booting ? "not-allowed" : "pointer",
            fontSize: "0.875rem",
          }}
        >
          New chat
        </button>
        <button
          type="button"
          onClick={() => void deleteCurrentChat()}
          disabled={loading || booting || !activeConversationId}
          style={{
            padding: "0.4rem 0.75rem",
            backgroundColor: "#ef4444",
            color: "white",
            border: "none",
            borderRadius: "0.375rem",
            cursor:
              loading || booting || !activeConversationId
                ? "not-allowed"
                : "pointer",
            fontSize: "0.875rem",
          }}
        >
          Delete chat
        </button>
      </div>

      <div style={{ flex: 1, overflow: "auto" }}>
        {booting && messages.length === 0 ? (
          <div style={{ textAlign: "center", color: "#666", marginTop: "2rem" }}>
            Loading conversation…
          </div>
        ) : messages.length === 0 ? (
          <div style={{ textAlign: "center", color: "#666", marginTop: "2rem" }}>
            Send a message to start this chat, or open another from <strong>Previous chats</strong>.
          </div>
        ) : (
          messages.map((msg) => (
            <div
              key={msg.id}
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: msg.role === "user" ? "flex-end" : "flex-start",
                marginBottom: "0.5rem",
              }}
            >
              <div
                style={{
                  maxWidth: "70%",
                  padding: "0.75rem 1rem",
                  borderRadius: "0.5rem",
                  backgroundColor: msg.role === "user" ? "#3b82f6" : "#e5e7eb",
                  color: msg.role === "user" ? "white" : "black",
                }}
              >
                {msg.content}
              </div>
            </div>
          ))
        )}
        {loading && (
          <div style={{ color: "#666", marginTop: "0.5rem" }}>
            Thinking...
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div style={{ display: "flex", gap: "0.5rem", marginTop: "1rem" }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a message..."
          disabled={!activeConversationId || booting}
          style={{
            flex: 1,
            padding: "0.75rem",
            borderRadius: "0.5rem",
            border: "1px solid #ddd",
            fontSize: "1rem",
          }}
        />
        <button
          type="button"
          onClick={() => void sendMessage()}
          disabled={loading || booting || !input.trim() || !activeConversationId}
          style={{
            padding: "0.75rem 1.5rem",
            borderRadius: "0.5rem",
            backgroundColor: loading ? "#9ca3af" : "#3b82f6",
            color: "white",
            border: "none",
            cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          Send
        </button>
      </div>
    </div>
  );
}
