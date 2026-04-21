import { useState, useRef, useEffect } from "react";
import { streamingChatCompletion, ChatMessage } from "../services/api";

interface Message extends ChatMessage {
  id: number;
}

interface ChatProps {
  selectedProject?: number;
}

export default function Chat(_props: ChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      id: Date.now(),
      role: "user",
      content: input,
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    // Initialize empty assistant message for streaming
    const assistantId = Date.now() + 1;
    setMessages((prev) => [...prev, { id: assistantId, role: "assistant", content: "" }]);

    try {
      const request = {
        model: "llama3.2",
        messages: [
          ...messages.map((m) => ({ role: m.role as "user" | "assistant", content: m.content })),
          { role: "user", content: input } as ChatMessage,
        ],
      };

      // Use streaming endpoint
      let fullContent = "";
      for await (const chunk of streamingChatCompletion(request)) {
        fullContent += chunk;
        // Update the assistant message as content arrives
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantId ? { ...msg, content: fullContent } : msg
          )
        );
      }

      // If no content was received, show fallback
      if (!fullContent) {
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === assistantId
              ? { ...msg, content: "Sorry, I didn't get a response." }
              : msg
          )
        );
      }
    } catch (error) {
      console.error("Error:", error);
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantId
            ? { ...msg, content: "Error: Could not connect to chat." }
            : msg
        )
      );
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div style={{ flex: 1, display: "flex", flexDirection: "column", padding: "1rem" }}>
      <div style={{ flex: 1, overflow: "auto" }}>
        {messages.length === 0 ? (
          <div style={{ textAlign: "center", color: "#666", marginTop: "2rem" }}>
            Send a message to start chatting
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
          style={{
            flex: 1,
            padding: "0.75rem",
            borderRadius: "0.5rem",
            border: "1px solid #ddd",
            fontSize: "1rem",
          }}
        />
        <button
          onClick={sendMessage}
          disabled={loading || !input.trim()}
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