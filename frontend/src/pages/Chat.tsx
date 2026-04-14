import { useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import ChatContainer from "@/components/chat/ChatContainer";
import { useChatStore } from "@/stores/chatStore";
import { sessionApi } from "@/api/session";
import type { Session } from "@/types/session";

export default function Chat() {
  const { setCurrentSession, setMessages, currentSession } = useChatStore();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const handleSessionSelect = async (session: Session) => {
    // 设置当前会话并加载消息
    setCurrentSession(session);

    // 加载会话详情
    try {
      const detail = await sessionApi.get(session.id);
      setMessages(detail.messages);
    } catch (error) {
      console.error("Failed to load session:", error);
    }
  };

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {/* 左侧边栏 */}
      <div
        className={`${
          sidebarOpen ? "w-64" : "w-0"
        } transition-all duration-300 overflow-hidden`}
      >
        <Sidebar onSessionSelect={handleSessionSelect} />
      </div>

      {/* 右侧聊天区域 */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* 顶部栏 */}
        <div className="h-14 border-b flex items-center justify-between px-4 bg-background">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 hover:bg-accent rounded-lg"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d={sidebarOpen ? "M11 19l-7-7 7-7" : "M13 5l7 7-7 7M5 5l7 7-7 7"}
                />
              </svg>
            </button>
            <h1 className="text-lg font-semibold">
              {currentSession?.title || "新对话"}
            </h1>
          </div>
          <div className="text-sm text-muted-foreground">
            {currentSession?.mode === "research" ? "研究模式" : "聊天模式"}
          </div>
        </div>

        {/* 聊天容器 */}
        <ChatContainer />
      </div>
    </div>
  );
}
