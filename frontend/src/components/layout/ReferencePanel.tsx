import { X, BookOpen } from "lucide-react";
import { useReferenceStore } from "@/stores/referenceStore";
import { ReferenceCard } from "@/components/common/ReferenceCard";

interface ReferencePanelProps {
  isOpen: boolean;
  onClose: () => void;
  className?: string;
}

export const ReferencePanel: React.FC<ReferencePanelProps> = ({
  isOpen,
  onClose,
  className,
}) => {
  const { activeCitations, highlightedId, setHighlightedId } = useReferenceStore();

  return (
    <aside
      className={`flex flex-col bg-background border-l transition-all duration-300 ease-in-out transform ${
        isOpen ? "translate-x-0 opacity-100" : "translate-x-full opacity-0"
      } ${className}`}
    >
      {/* 头部 */}
      <div className="flex items-center justify-between p-4 border-b">
        <h2 className="text-lg font-semibold text-foreground">引用来源</h2>
        <button
          onClick={onClose}
          className="p-1 rounded-lg hover:bg-accent transition-colors"
        >
          <X className="w-5 h-5 text-muted-foreground" />
        </button>
      </div>

      {/* 引用列表 */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {activeCitations.length === 0 ? (
          <div className="text-center text-muted-foreground py-8">
            <BookOpen className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>暂无引用</p>
            <p className="text-sm mt-1">点击消息中的引用标记查看来源</p>
          </div>
        ) : (
          activeCitations.map((citation) => (
            <ReferenceCard
              key={citation.id}
              citation={citation}
              isHighlighted={citation.id === highlightedId}
              onClick={() => setHighlightedId(citation.id)}
            />
          ))
        )}
      </div>
    </aside>
  );
};
