import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { User, Bot, Loader2, CheckCircle } from "lucide-react";
import { CitationLink } from "./CitationLink";
import { useReferenceStore } from "@/stores/referenceStore";
import type { Message } from "@/types/session";

interface MessageBubbleProps {
  message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const { setActiveCitations, setPanelOpen, setHighlightedId } = useReferenceStore();

  // 判断是否有思维链内容
  const hasThinking = message.thinking !== undefined &&
                      message.thinking !== null &&
                      message.thinking.length > 0;

  // 判断思考是否已结束：当有内容时说明思考已完成
  const thinkingFinished = message.content && message.content.length > 0;

  // 处理引用点击
  const handleCitationClick = (citationId: string) => {
    if (message.citations) {
      setActiveCitations(message.citations);
      setPanelOpen(true);
      setHighlightedId(citationId);
    }
  };

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      {/* 头像 */}
      <div
        className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
          isUser ? "bg-primary/10 mr-3" : "bg-muted mr-3"
        }`}
      >
        {isUser ? (
          <User className="w-5 h-5 text-primary" />
        ) : (
          <Bot className="w-5 h-5 text-muted-foreground" />
        )}
      </div>

      <div
        className={`max-w-[70%] rounded-2xl px-4 py-3 ${
          isUser
            ? "bg-primary text-primary-foreground"
            : "bg-muted"
        }`}
      >
        {/* 思维链显示区域 - 只要有内容就显示 */}
        {!isUser && hasThinking && message.thinking && (
          <div
            className="bg-white rounded-lg p-3 mb-2 text-xs text-gray-500 border border-gray-200"
            style={{ overflow: 'visible', minHeight: 'auto' }}
          >
            {/* 思考中的指示器 */}
            <div className="flex items-center gap-1 mb-1">
              {thinkingFinished ? (
                <>
                  <CheckCircle className="w-3 h-3 text-green-500" />
                  <span className="text-xs text-green-500">思考结束</span>
                </>
              ) : (
                <>
                  <Loader2 className="w-3 h-3 animate-spin" />
                  <span className="text-xs text-gray-400">思考中</span>
                </>
              )}
            </div>
            <div
              className="whitespace-pre-wrap break-words"
              style={{ overflow: 'visible', height: 'auto' }}
            >
              {message.thinking}
            </div>
          </div>
        )}

        <div className={`${isUser ? "" : "prose prose-sm max-w-none"}`}>
          {isUser ? (
            <p className="whitespace-pre-wrap break-words text-sm">{message.content}</p>
          ) : (
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content}
            </ReactMarkdown>
          )}
        </div>

        {/* 引用标记（仅助手消息） */}
        {!isUser && message.citations && message.citations.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-3 pt-3 border-t border-border/50">
            {message.citations.map((citation) => (
              <CitationLink
                key={citation.id}
                index={citation.index}
                onClick={() => handleCitationClick(citation.id)}
              />
            ))}
          </div>
        )}

        <div className="text-xs text-muted-foreground mt-1">
          {new Date(message.created_at).toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
}
