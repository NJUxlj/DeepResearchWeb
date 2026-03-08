import { useEffect, useRef } from "react";
import MessageBubble from "./MessageBubble";
import InputBar from "./InputBar";
import type { Message } from "@/types/session";

interface ChatWindowProps {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  onSendMessage: (content: string) => void;
  onStop?: () => void;
}

export default function ChatWindow({
  messages,
  isLoading,
  error,
  onSendMessage,
  onStop,
}: ChatWindowProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 自动滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex flex-col h-full">
      {/* 消息列表 */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-4xl mx-auto">
          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full min-h-[200px]">
              <div className="text-center text-muted-foreground">
                <p className="text-lg mb-2">欢迎使用 DeepResearchWeb</p>
                <p className="text-sm">开始一个新对话吧</p>
              </div>
            </div>
          ) : (
            messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))
          )}
          {error && (
            <div className="bg-destructive/10 border border-destructive text-destructive rounded-lg p-3 mb-4">
              {error}
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* 输入栏 */}
      <InputBar
        onSend={onSendMessage}
        onStop={onStop}
        isLoading={isLoading}
      />
    </div>
  );
}
