import { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { MessageSquare, Settings, Wrench, Zap, Server, User, Plus, Trash2, LogOut } from "lucide-react";
import { useSessionStore } from "@/stores/sessionStore";
import { useAuthStore } from "@/stores/authStore";
import { useChatStore } from "@/stores/chatStore";
import type { Session } from "@/types/session";
import { sessionApi } from "@/api/session";

interface SidebarProps {
  className?: string;
  onSessionSelect?: (session: Session) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ className, onSessionSelect }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { sessions, setSessions, addSession, removeSession, setLoading } = useSessionStore();
  const { currentSession, clearChat, setCurrentSession } = useChatStore();
  const { user, logout } = useAuthStore();
  const [isCreating, setIsCreating] = useState(true);

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    setLoading(true);
    try {
      const response = await sessionApi.list({ page: 1, page_size: 50 });
      setSessions(response.items);
    } catch (error) {
      console.error("Failed to load sessions:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleNewChat = async () => {
    setIsCreating(true);
    try {
      const session = await sessionApi.create({
        title: "新对话",
        mode: "chat",
      });
      addSession(session);
      setCurrentSession(session);
      onSessionSelect?.(session);
      navigate("/chat");
    } catch (error) {
      console.error("Failed to create session:", error);
    } finally {
      setIsCreating(false);
    }
  };

  const handleSelectSession = async (session: Session) => {
    setCurrentSession(session);
    try {
      const detail = await sessionApi.get(session.id);
      useChatStore.getState().setMessages(detail.messages);
    } catch (error) {
      console.error("Failed to load session:", error);
    }
    onSessionSelect?.(session);
    navigate(`/chat/${session.id}`);
  };

  const handleDeleteSession = async (e: React.MouseEvent, sessionId: number) => {
    e.stopPropagation();
    if (!confirm("确定要删除这个会话吗？")) return;

    try {
      await sessionApi.delete(sessionId);
      removeSession(sessionId);
      if (currentSession?.id === sessionId) {
        clearChat();
      }
    } catch (error) {
      console.error("Failed to delete session:", error);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days === 0) return "今天";
    if (days === 1) return "昨天";
    if (days < 7) return `${days} 天前`;
    return date.toLocaleDateString();
  };

  const isActive = (path: string) => location.pathname.startsWith(path);

  return (
    <aside className={`flex flex-col bg-card border-r ${className}`}>
      {/* Logo */}
      <div className="p-4 border-b">
        <h1 className="text-xl font-bold text-primary">DeepResearch</h1>
      </div>

      {/* 新建对话按钮 */}
      <div className="p-3">
        <button
          onClick={handleNewChat}
          disabled={isCreating}
          className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50"
        >
          <Plus className="w-4 h-4" />
          <span>新建对话</span>
        </button>
      </div>

      {/* 会话列表 */}
      <div className="flex-1 overflow-y-auto">
        <h3 className="text-xs font-medium text-muted-foreground uppercase mb-2 px-3">
          历史会话
        </h3>
        <div className="space-y-1 px-2">
          {sessions.map((session) => (
            <div
              key={session.id}
              onClick={() => handleSelectSession(session)}
              className={`group flex items-center gap-2 rounded-lg px-3 py-2 cursor-pointer transition-colors ${
                currentSession?.id === session.id
                  ? "bg-accent"
                  : "hover:bg-accent/50"
              }`}
            >
              {session.mode === "research" ? (
                <Zap className="w-4 h-4 text-amber-500 flex-shrink-0" />
              ) : (
                <MessageSquare className="w-4 h-4 text-muted-foreground flex-shrink-0" />
              )}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">
                  {session.title}
                </p>
                <p className="text-xs text-muted-foreground">
                  {formatDate(session.updated_at)}
                </p>
              </div>
              <button
                onClick={(e) => handleDeleteSession(e, session.id)}
                className="opacity-0 group-hover:opacity-100 p-1 hover:bg-destructive/10 rounded transition-opacity"
              >
                <Trash2 className="h-3 w-3 text-destructive" />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* 配置导航 */}
      <div className="p-3 border-t space-y-1">
        <NavButton
          icon={<Wrench className="w-4 h-4" />}
          label="工具配置"
          isActive={isActive("/config/tools")}
          onClick={() => navigate("/config/tools")}
        />
        <NavButton
          icon={<Zap className="w-4 h-4" />}
          label="Skills"
          isActive={isActive("/config/skills")}
          onClick={() => navigate("/config/skills")}
        />
        <NavButton
          icon={<Server className="w-4 h-4" />}
          label="MCP 配置"
          isActive={isActive("/config/mcp")}
          onClick={() => navigate("/config/mcp")}
        />
        <NavButton
          icon={<Settings className="w-4 h-4" />}
          label="设置"
          isActive={isActive("/settings")}
          onClick={() => navigate("/settings")}
        />
      </div>

      {/* 用户信息 */}
      <div className="p-3 border-t">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
            <User className="w-4 h-4 text-primary" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-foreground truncate">
              {user?.username}
            </p>
          </div>
          <button
            onClick={logout}
            className="text-xs text-muted-foreground hover:text-destructive"
            title="退出登录"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
};

interface NavButtonProps {
  icon: React.ReactNode;
  label: string;
  isActive?: boolean;
  onClick: () => void;
}

const NavButton: React.FC<NavButtonProps> = ({ icon, label, isActive, onClick }) => (
  <button
    onClick={onClick}
    className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
      isActive
        ? "bg-accent text-accent-foreground"
        : "text-muted-foreground hover:bg-accent hover:text-foreground"
    }`}
  >
    {icon}
    <span>{label}</span>
  </button>
);
