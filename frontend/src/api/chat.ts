import type { ChatRequest, ChatResponse, Citation } from "@/types/session";

const API_BASE_URL = import.meta.env.VITE_API_URL || "/api/v1";

export type StreamCallback = {
  onChunk?: (content: string) => void;
  onThinking?: (content: string) => void;
  onCitations?: (citations: Citation[]) => void;
  onDone?: (messageId: number) => void;
  onError?: (error: string) => void;
};

/**
 * 使用 Fetch API 创建 SSE 流式连接
 * @param request 聊天请求
 * @param callbacks 回调函数
 * @returns abort 函数
 */
export function createChatStream(
  request: ChatRequest,
  callbacks: StreamCallback
): () => void {
  const params = new URLSearchParams();
  if (request.session_id) {
    params.append("session_id", String(request.session_id));
  }
  params.append("message", request.message);
  params.append("stream", "true");

  const token = localStorage.getItem("token");
  const url = `${API_BASE_URL}/chat/stream?${params.toString()}`;

  const controller = new AbortController();
  let isAborted = false;
  let isFinished = false;

  const cleanup = () => {
    if (!isFinished) {
      isFinished = true;
      // 确保即使没有收到 done 事件，也调用 onDone
      callbacks.onDone?.(-1);
    }
  };

  fetch(url, {
    method: "GET",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    signal: controller.signal,
  })
    .then(async (response) => {
      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: "Request failed" }));
        callbacks.onError?.(error.detail || "Request failed");
        cleanup();
        return;
      }

      if (!response.body) {
        callbacks.onError?.("No response body");
        cleanup();
        return;
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      const readChunk = () => {
        reader.read().then(({ done, value }) => {
          if (done || isAborted) {
            // Stream finished
            if (!isFinished) {
              cleanup();
            }
            return;
          }

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n\n");
          buffer = lines.pop() || "";

          for (const event of lines) {
            if (isAborted) break;

            const eventLines = event.split("\n");
            let eventType = "";
            let eventData = "";

            for (const line of eventLines) {
              if (line.startsWith("event:")) {
                eventType = line.slice(6).trim();
              } else if (line.startsWith("data:")) {
                eventData = line.slice(5).trim();
              }
            }

            if (eventData) {
              try {
                const data = JSON.parse(eventData);

                switch (eventType) {
                  case "thinking":
                    callbacks.onThinking?.(data.content || "");
                    break;
                  case "chunk":
                    callbacks.onChunk?.(data.content || "");
                    break;
                  case "citations":
                    callbacks.onCitations?.(data.citations || []);
                    break;
                  case "done":
                    callbacks.onDone?.(data.message_id);
                    isFinished = true;
                    break;
                  case "error":
                    callbacks.onError?.(data.error || "Unknown error");
                    isFinished = true;
                    break;
                  default:
                    // 处理默认消息
                    break;
                }
              } catch (e) {
                console.error("Failed to parse SSE data:", e);
              }
            }
          }

          if (!isAborted) {
            readChunk();
          }
        });
      };

      readChunk();
    })
    .catch((error) => {
      if (!isAborted) {
        console.error("Fetch error:", error);
        callbacks.onError?.("Connection error");
        cleanup();
      }
    });

  // 返回清理函数
  return () => {
    isAborted = true;
    controller.abort();
  };
}

/**
 * 发送消息（非流式）
 */
export async function sendMessage(request: ChatRequest): Promise<ChatResponse> {
  const token = localStorage.getItem("token");

  const response = await fetch(`${API_BASE_URL}/chat/message`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail || "Request failed");
  }

  return response.json();
}
