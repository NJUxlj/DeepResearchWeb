import { useCallback, useRef, useState } from "react";

interface SSEOptions {
  onMessage?: (event: string, data: unknown) => void;
  onError?: (error: Event) => void;
  onComplete?: () => void;
}

export function useSSE() {
  const [isConnected, setIsConnected] = useState(false);
  const eventSourceRef = useRef<EventSource | null>(null);

  const connect = useCallback((url: string, options: SSEOptions = {}) => {
    // 关闭已有连接
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    const eventSource = new EventSource(url);
    eventSourceRef.current = eventSource;
    setIsConnected(true);

    eventSource.onopen = () => {
      console.log("SSE connected");
    };

    // 监听标准消息
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        options.onMessage?.("message", data);
      } catch {
        options.onMessage?.("message", event.data);
      }
    };

    // 监听自定义事件
    const events = ["message", "chunk", "citations", "error", "done"];
    events.forEach((eventName) => {
      eventSource.addEventListener(eventName, (event) => {
        try {
          const data = JSON.parse(event.data);
          options.onMessage?.(eventName, data);

          if (eventName === "done") {
            options.onComplete?.();
            disconnect();
          }
        } catch {
          options.onMessage?.(eventName, event.data);
        }
      });
    });

    eventSource.onerror = (error) => {
      console.error("SSE error:", error);
      options.onError?.(error);
      setIsConnected(false);
    };

    return eventSource;
  }, []);

  const disconnect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
      setIsConnected(false);
    }
  }, []);

  return {
    connect,
    disconnect,
    isConnected,
  };
}
