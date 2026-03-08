import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { User, Bot } from "lucide-react";
import { CitationLink } from "./CitationLink";
import { useReferenceStore } from "@/stores/referenceStore";
import type { Message } from "@/types/session";

interface MessageBubbleProps {
  message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const { setActiveCitations, setPanelOpen, setHighlightedId } = useReferenceStore();

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
