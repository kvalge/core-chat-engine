/** SSE client for streaming responses. */
export class SSEClient {
  private eventSource: EventSource | null = null;
  private onMessage: (data: string) => void;
  private onError: (error: string) => void;
  private onDone: () => void;

  constructor(
    onMessage: (data: string) => void,
    onError: (error: string) => void,
    onDone: () => void
  ) {
    this.onMessage = onMessage;
    this.onError = onError;
    this.onDone = onDone;
  }

  connect(url: string): void {
    this.eventSource = new EventSource(url);

    this.eventSource.onmessage = (event) => {
      const data = event.data;
      if (data === "[DONE]") {
        this.onDone();
        return;
      }
      try {
        const parsed = JSON.parse(data);
        if (parsed.choices?.[0]?.delta?.content) {
          this.onMessage(parsed.choices[0].delta.content);
        } else if (parsed.error) {
          this.onError(parsed.error.message);
        }
      } catch {
        // Ignore parse errors
      }
    };

    this.eventSource.onerror = () => {
      this.onError("Connection closed");
    };
  }

  close(): void {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
  }
}

export async function* streamingGenerator(
  url: string
): AsyncGenerator<string, void, unknown> {
  const response = await fetch(url);
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