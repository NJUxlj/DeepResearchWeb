import { useCallback, useRef } from "react";
import { useChatStore } from "@/stores/chatStore";
import { createChatStream } from "@/api/chat";
import { sessionApi } from "@/api/session";
import type { ChatRequest, Message } from "@/types/session";

export function useChat() {
  const {
    currentSession,
    messages,
    isLoading,
    error,
    setCurrentSession,
    updateCurrentSessionId,
    setMessages,
    addMessage,
    updateLastMessage,
    updateLastMessageThinking,
    setLoading,
    setError,
    clearChat,
  } = useChatStore();

  const cleanupRef = useRef<(() => void) | null>(null);

  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim() || isLoading) return;

      // 清理之前的连接
      if (cleanupRef.current) {
        cleanupRef.current();
        cleanupRef.current = null;
      }

      setLoading(true);
      setError(null);

      // 添加用户消息
      const userMessage: Message = {
        id: Date.now(),
        session_id: currentSession?.id || 0,
        role: "user",
        content: content.trim(),
        created_at: new Date().toISOString(),
      };
      addMessage(userMessage);

      // 添加空的助手消息占位
      const assistantMessage: Message = {
        id: Date.now() + 1,
        session_id: currentSession?.id || 0,
        role: "assistant",
        content: "",
        thinking: "",
        created_at: new Date().toISOString(),
      };
      addMessage(assistantMessage);

      try {
        const request: ChatRequest = {
          session_id: currentSession?.id,
          message: content.trim(),
          stream: true,
        };

        const currentContent: string[] = [];
        const currentThinking: string[] = [];

        cleanupRef.current = createChatStream(request, {
          onThinking: (thinkingChunk) => {
            console.log("[Chat] Received thinking chunk:", thinkingChunk);
            currentThinking.push(thinkingChunk);
            updateLastMessageThinking(currentThinking.join(""));
            console.log("[Chat] Updated thinking:", currentThinking.join(""));
          },
          onChunk: (chunk) => {
            currentContent.push(chunk);
            updateLastMessage(currentContent.join(""));
          },
          onCitations: (_citations) => {
            // TODO: 更新消息的引用信息
          },
          onDone: (_messageId) => {
            console.log("[Chat] Stream done, messageId:", _messageId);
            setLoading(false);
          },
          onError: (errorMsg) => {
            console.error("[Chat] Stream error:", errorMsg);
            setError(errorMsg);
            setLoading(false);
          },
          onSessionId: (sessionId) => {
            console.log("[Chat] Received new session ID:", sessionId);
            // 更新当前会话的 ID
            updateCurrentSessionId(sessionId);
          },
        });
      } catch (err) {
        console.error("[Chat] Send message error:", err);
        setError(err instanceof Error ? err.message : "Failed to send message");
        setLoading(false);
      }
    },
    [
      currentSession,
      messages,
      isLoading,
      setLoading,
      setError,
      addMessage,
      updateLastMessage,
      updateLastMessageThinking,
      updateCurrentSessionId,
    ]
  );

  const loadSession = useCallback(
    async (sessionId: number) => {
      setLoading(true);
      setError(null);

      try {
        const session = await sessionApi.get(sessionId);
        console.log("[Chat] Loaded session messages:", session.messages);
        setCurrentSession(session);
        setMessages(session.messages);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load session");
      } finally {
        setLoading(false);
      }
    },
    [setCurrentSession, setMessages, setLoading, setError]
  );

  const createNewSession = useCallback(
    async (title: string = "New Chat") => {
      try {
        const session = await sessionApi.create({
          title,
          mode: "chat",
        });
        setCurrentSession(session);
        setMessages([]);
        return session;
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to create session");
        return null;
      }
    },
    [setCurrentSession, setMessages, setError]
  );

  const deleteSession = useCallback(
    async (sessionId: number) => {
      try {
        await sessionApi.delete(sessionId);
        if (currentSession?.id === sessionId) {
          clearChat();
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to delete session");
      }
    },
    [currentSession, clearChat, setError]
  );

  const stopStream = useCallback(() => {
    if (cleanupRef.current) {
      cleanupRef.current();
      cleanupRef.current = null;
    }
    setLoading(false);
  }, [setLoading]);

  return {
    currentSession,
    messages,
    isLoading,
    error,
    sendMessage,
    loadSession,
    createNewSession,
    deleteSession,
    stopStream,
    clearChat,
  };
}
