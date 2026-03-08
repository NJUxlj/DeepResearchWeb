/**
 * 引用来源类型
 */
export type CitationSourceType = "web" | "mcp" | "memory" | "document";

/**
 * 引用卡片数据
 */
export interface Citation {
  id: string;
  index: number;
  url: string;
  title: string;
  snippet: string;
  source_type: CitationSourceType;
  favicon?: string;
}

/**
 * 引用面板状态
 */
export interface ReferenceState {
  activeCitations: Citation[];
  highlightedId: string | null;
  isPanelOpen: boolean;
  setActiveCitations: (citations: Citation[]) => void;
  addCitation: (citation: Citation) => void;
  setHighlightedId: (id: string | null) => void;
  setPanelOpen: (open: boolean) => void;
  highlightAndScroll: (id: string) => void;
  clearCitations: () => void;
}

/**
 * 工具配置类型
 */
export interface ToolConfig {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
  config?: Record<string, unknown>;
}

/**
 * Skill 配置类型
 */
export interface SkillConfig {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
  config?: Record<string, unknown>;
}

/**
 * MCP 服务器配置类型
 */
export interface MCPConfig {
  id: string;
  name: string;
  type: "stdio" | "http";
  config: {
    command?: string;
    url?: string;
    env?: Record<string, string>;
  };
  enabled: boolean;
}
