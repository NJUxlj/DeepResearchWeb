import { create } from "zustand";
import type { Session } from "@/types/session";

interface SessionState {
  // 会话列表
  sessions: Session[];
  total: number;
  page: number;
  pageSize: number;
  isLoading: boolean;

  // 方法
  setSessions: (sessions: Session[]) => void;
  addSession: (session: Session) => void;
  updateSession: (session: Session) => void;
  removeSession: (sessionId: number) => void;
  setPagination: (total: number, page: number, pageSize: number) => void;
  setLoading: (loading: boolean) => void;
}

export const useSessionStore = create<SessionState>((set) => ({
  sessions: [],
  total: 0,
  page: 1,
  pageSize: 20,
  isLoading: false,

  setSessions: (sessions) => set({ sessions }),

  addSession: (session) =>
    set((state) => ({ sessions: [session, ...state.sessions] })),

  updateSession: (session) =>
    set((state) => ({
      sessions: state.sessions.map((s) =>
        s.id === session.id ? session : s
      ),
    })),

  removeSession: (sessionId) =>
    set((state) => ({
      sessions: state.sessions.filter((s) => s.id !== sessionId),
    })),

  setPagination: (total, page, pageSize) =>
    set({ total, page, pageSize }),

  setLoading: (loading) => set({ isLoading: loading }),
}));
