import { create } from "zustand";
import type { Message, Session } from "@/types/session";

interface ChatState {
  // 当前会话
  currentSession: Session | null;
  messages: Message[];
  isLoading: boolean;
  error: string | null;

  // 方法
  setCurrentSession: (session: Session | null) => void;
  setMessages: (messages: Message[]) => void;
  addMessage: (message: Message) => void;
  updateLastMessage: (content: string) => void;
  updateLastMessageThinking: (thinking: string) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearChat: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  currentSession: null,
  messages: [],
  isLoading: false,
  error: null,

  setCurrentSession: (session) => set({ currentSession: session }),

  setMessages: (messages) => set({ messages }),

  addMessage: (message) =>
    set((state) => ({ messages: [...state.messages, message] })),

  updateLastMessage: (content) =>
    set((state) => {
      const messages = [...state.messages];
      if (messages.length > 0) {
        const lastMsg = messages[messages.length - 1];
        if (lastMsg.role === "assistant") {
          messages[messages.length - 1] = { ...lastMsg, content };
        }
      }
      return { messages };
    }),

  updateLastMessageThinking: (thinking) =>
    set((state) => {
      const messages = [...state.messages];
      if (messages.length > 0) {
        const lastMsg = messages[messages.length - 1];
        if (lastMsg.role === "assistant") {
          messages[messages.length - 1] = { ...lastMsg, thinking };
        }
      }
      return { messages };
    }),

  setLoading: (loading) => set({ isLoading: loading }),

  setError: (error) => set({ error }),

  clearChat: () =>
    set({ currentSession: null, messages: [], error: null }),
}));
