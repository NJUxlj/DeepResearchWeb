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
  id: number;
  name: string;
  description: string;
  tool_type: string;
  enabled: boolean;
  config?: Record<string, unknown>;
}

/**
 * Skill 配置类型
 */
export interface SkillConfig {
  id: number;
  name: string;
  description: string;
  trigger_keywords: string;
  system_prompt: string;
  required_tools: string[];
  enabled: boolean;
  config?: Record<string, unknown>;
}

/**
 * MCP 服务器配置类型
 * 与后端 MCPServerConfigBase 保持一致
 */
export interface MCPConfig {
  id: number;
  name: string;
  description?: string;
  transport: "stdio" | "http";
  command: string | null;
  args: string[];
  env: Record<string, string>;
  url: string | null;
  enabled: boolean;
}
