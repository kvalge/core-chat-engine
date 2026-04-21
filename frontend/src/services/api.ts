/** API client for backend communication. */
const API_BASE = "/v1/chat";

export interface ChatMessage {
  role: "system" | "user" | "assistant";
  content: string;
}

export interface ChatCompletionRequest {
  model: string;
  messages: ChatMessage[];
  temperature?: number;
  max_tokens?: number;
  stream?: boolean;
}

export interface ChatCompletionResponse {
  id: string;
  object: string;
  created: number;
  model: string;
  choices: Array<{
    index: number;
    message: {
      role: string;
      content: string;
    };
    finish_reason: string;
  }>;
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

export async function sendChatCompletion(
  request: ChatCompletionRequest
): Promise<ChatCompletionResponse> {
  const response = await fetch(`${API_BASE}/completions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

export async function* streamingChatCompletion(
  request: ChatCompletionRequest
): AsyncGenerator<string, void, unknown> {
  const response = await fetch(`${API_BASE}/completions/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...request, stream: true }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  const reader = response.body?.getReader();
  if (!reader) throw new Error("No response body");

  const decoder = new TextDecoder();
  let buffer = "";

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const data = line.slice(6);
          if (data === "[DONE]") return;
          try {
            const parsed = JSON.parse(data);
            const content = parsed.choices?.[0]?.delta?.content;
            if (content) yield content;
          } catch {
            // Skip invalid JSON
          }
        }
      }
    }
  } finally {
    reader.releaseLock();
  }
}

// Projects API
export interface Project {
  id: number;
  name: string;
  system_prompt: string;
  default_model: string;
  enabled_tools: string[];
  created_at: string;
  updated_at: string;
}

export async function listProjects(): Promise<Project[]> {
  const response = await fetch("/api/projects");
  if (!response.ok) throw new Error("Failed to fetch projects");
  return response.json();
}

export async function createProject(data: {
  name: string;
  system_prompt?: string;
  default_model?: string;
  enabled_tools?: string[];
}): Promise<Project> {
  const response = await fetch("/api/projects", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error("Failed to create project");
  return response.json();
}

export async function updateProject(
  id: number,
  data: Partial<Project>
): Promise<Project> {
  const response = await fetch(`/api/projects/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error("Failed to update project");
  return response.json();
}

export async function deleteProject(id: number): Promise<void> {
  const response = await fetch(`/api/projects/${id}`, { method: "DELETE" });
  if (!response.ok) throw new Error("Failed to delete project");
}

export async function getProject(id: number): Promise<Project> {
  const response = await fetch(`/api/projects/${id}`);
  if (!response.ok) throw new Error("Failed to fetch project");
  return response.json();
}

export interface Conversation {
  id: number;
  project_id: number;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface StoredMessage {
  id: number;
  role: string;
  content: string;
  tool_calls?: unknown;
  tool_results?: unknown;
  created_at: string;
}

export async function listConversations(projectId: number): Promise<Conversation[]> {
  const response = await fetch(`/api/projects/${projectId}/conversations`);
  if (!response.ok) throw new Error("Failed to list conversations");
  return response.json();
}

export async function createConversation(
  projectId: number,
  title: string
): Promise<Conversation> {
  const response = await fetch(`/api/projects/${projectId}/conversations`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error((err as { detail?: string }).detail || "Failed to create conversation");
  }
  return response.json();
}

export async function getConversationDetail(
  conversationId: number
): Promise<{ conversation: Conversation; messages: StoredMessage[] }> {
  const response = await fetch(`/api/conversations/${conversationId}`);
  if (!response.ok) throw new Error("Failed to load conversation");
  return response.json();
}

export async function appendMessage(
  conversationId: number,
  body: { role: string; content: string }
): Promise<StoredMessage> {
  const response = await fetch(`/api/conversations/${conversationId}/messages`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error((err as { detail?: string }).detail || "Failed to save message");
  }
  return response.json();
}

export async function deleteConversation(conversationId: number): Promise<void> {
  const response = await fetch(`/api/conversations/${conversationId}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error((err as { detail?: string }).detail || "Failed to delete conversation");
  }
}

/** Title for a new chat: locale date + time (used for first chat and "New chat"). */
export function newChatTitle(date: Date = new Date()): string {
  return date.toLocaleString(undefined, {
    dateStyle: "short",
    timeStyle: "medium",
  });
}

/** Ollama model tags commonly used locally (see project spec). */
export const OLLAMA_LOCAL_MODELS = ["llama3.2", "mistral"] as const;

// Backends API
export interface Backend {
  id: number;
  name: string;
  base_url: string;
  api_key?: string;
  models: string[];
  is_default: boolean;
  created_at: string;
}

export async function listBackends(): Promise<Backend[]> {
  const response = await fetch("/api/backends");
  if (!response.ok) throw new Error("Failed to fetch backends");
  return response.json();
}

export async function createBackend(data: {
  name: string;
  base_url: string;
  api_key?: string;
  models?: string[];
  is_default?: boolean;
}): Promise<Backend> {
  const response = await fetch("/api/backends", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error("Failed to create backend");
  return response.json();
}

export async function testBackend(
  id: number
): Promise<{ success: boolean; message: string; models: string[] }> {
  const response = await fetch(`/api/backends/${id}/test`, { method: "POST" });
  if (!response.ok) throw new Error("Failed to test backend");
  return response.json();
}

export async function deleteBackend(id: number): Promise<void> {
  const response = await fetch(`/api/backends/${id}`, { method: "DELETE" });
  if (!response.ok) throw new Error("Failed to delete backend");
}