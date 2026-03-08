import { ExternalLink, Globe, Database, Brain, FileText } from "lucide-react";
import type { Citation, CitationSourceType } from "@/types/citation";

interface ReferenceCardProps {
  citation: Citation;
  isHighlighted?: boolean;
  onClick?: () => void;
}

const sourceIcons: Record<CitationSourceType, React.ComponentType<{ className?: string }>> = {
  web: Globe,
  mcp: Database,
  memory: Brain,
  document: FileText,
};

const sourceLabels: Record<CitationSourceType, string> = {
  web: "网页",
  mcp: "MCP",
  memory: "记忆",
  document: "文档",
};

export const ReferenceCard: React.FC<ReferenceCardProps> = ({
  citation,
  isHighlighted = false,
  onClick,
}) => {
  const Icon = sourceIcons[citation.source_type] || Globe;

  return (
    <div
      onClick={onClick}
      className={`p-4 rounded-lg border cursor-pointer transition-all ${
        isHighlighted
          ? "border-primary bg-primary/5 ring-2 ring-primary/20"
          : "border-border hover:border-input hover:bg-accent/50"
      }`}
    >
      {/* 头部 */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="flex items-center justify-center w-6 h-6 rounded-full bg-primary/10 text-primary text-sm font-medium">
            {citation.index}
          </span>
          <Icon className="w-4 h-4 text-muted-foreground" />
          <span className="text-xs font-medium text-muted-foreground uppercase">
            {sourceLabels[citation.source_type]}
          </span>
        </div>
        {citation.url && (
          <a
            href={citation.url}
            target="_blank"
            rel="noopener noreferrer"
            className="p-1 rounded hover:bg-accent transition-colors"
            onClick={(e) => e.stopPropagation()}
          >
            <ExternalLink className="w-4 h-4 text-muted-foreground" />
          </a>
        )}
      </div>

      {/* 标题 */}
      <h3 className="mt-2 font-medium text-foreground line-clamp-2">
        {citation.title}
      </h3>

      {/* URL */}
      {citation.url && (
        <p className="mt-1 text-xs text-muted-foreground truncate">
          {citation.url}
        </p>
      )}

      {/* 摘要 */}
      <p className="mt-2 text-sm text-muted-foreground line-clamp-3">
        {citation.snippet}
      </p>
    </div>
  );
};
