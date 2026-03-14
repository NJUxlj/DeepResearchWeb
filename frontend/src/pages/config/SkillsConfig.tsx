import { useState, useEffect } from "react";
import { Zap, Plus, Trash2, Power, PowerOff, X, Pencil } from "lucide-react";
import { skillsApi } from "@/api/skills";
import type { SkillConfig } from "@/types/citation";

export function SkillsConfig() {
  const [skills, setSkills] = useState<SkillConfig[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editingSkill, setEditingSkill] = useState<SkillConfig | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  useEffect(() => {
    loadSkills();
  }, []);

  const loadSkills = async () => {
    setIsLoading(true);
    try {
      const response = await skillsApi.list();
      setSkills(response.items);
    } catch (err) {
      setError("加载 Skills 列表失败");
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggle = async (id: number, enabled: boolean) => {
    try {
      await skillsApi.toggle(id, !enabled);
      setSkills((prev) =>
        prev.map((skill) =>
          skill.id === id ? { ...skill, enabled: !enabled } : skill
        )
      );
    } catch (err) {
      console.error("Failed to toggle skill:", err);
      alert("切换 Skill 状态失败，请重试");
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("确定要删除这个 Skill 吗？")) return;
    try {
      await skillsApi.delete(id);
      setSkills((prev) => prev.filter((skill) => skill.id !== id));
    } catch (err) {
      console.error("Failed to delete skill:", err);
    }
  };

  const handleCreateSkill = async (data: Partial<SkillConfig>) => {
    setIsSubmitting(true);
    setSubmitError(null);
    try {
      await skillsApi.create(data as Omit<SkillConfig, "id">);
      setIsModalOpen(false);
      loadSkills();
    } catch (err: any) {
      setSubmitError(err?.response?.data?.detail || "创建 Skill 失败");
      console.error("Failed to create skill:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleEdit = (skill: SkillConfig) => {
    setEditingSkill(skill);
    setIsEditModalOpen(true);
  };

  const handleUpdateSkill = async (data: Partial<SkillConfig>) => {
    if (!editingSkill) return;
    setIsSubmitting(true);
    setSubmitError(null);
    try {
      await skillsApi.update(editingSkill.id, data);
      setIsEditModalOpen(false);
      setEditingSkill(null);
      loadSkills();
    } catch (err: any) {
      setSubmitError(err?.response?.data?.detail || "更新 Skill 失败");
      console.error("Failed to update skill:", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-muted-foreground">加载中...</div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Zap className="w-6 h-6 text-primary" />
          <h1 className="text-2xl font-bold">Skills 配置</h1>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90"
        >
          <Plus className="w-4 h-4" />
          添加 Skill
        </button>
      </div>

      {error && (
        <div className="bg-destructive/10 border border-destructive text-destructive rounded-lg p-3 mb-4">
          {error}
        </div>
      )}

      {skills.length === 0 ? (
        <div className="text-center text-muted-foreground py-12">
          <Zap className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>暂无 Skills 配置</p>
          <p className="text-sm mt-1">点击添加按钮创建新 Skill</p>
        </div>
      ) : (
        <div className="space-y-3">
          {skills.map((skill) => (
            <div
              key={skill.id}
              className={`p-4 rounded-lg border bg-card ${
                skill.enabled ? "border-primary" : "border-border"
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg ${skill.enabled ? "bg-primary/10" : "bg-muted"}`}>
                    <Zap className={`w-5 h-5 ${skill.enabled ? "text-primary" : "text-muted-foreground"}`} />
                  </div>
                  <div>
                    <h3 className="font-medium">{skill.name}</h3>
                    <p className="text-sm text-muted-foreground">{skill.description}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleEdit(skill)}
                    className="p-2 text-muted-foreground hover:text-primary hover:bg-primary/10 rounded-lg transition-colors"
                    title="编辑"
                  >
                    <Pencil className="w-5 h-5" />
                  </button>
                  <button
                    onClick={() => handleToggle(skill.id, skill.enabled)}
                    className={`p-2 rounded-lg transition-colors ${
                      skill.enabled
                        ? "text-primary hover:bg-primary/10"
                        : "text-muted-foreground hover:bg-muted"
                    }`}
                    title={skill.enabled ? "禁用" : "启用"}
                  >
                    {skill.enabled ? <Power className="w-5 h-5" /> : <PowerOff className="w-5 h-5" />}
                  </button>
                  <button
                    onClick={() => handleDelete(skill.id)}
                    className="p-2 text-muted-foreground hover:text-destructive hover:bg-destructive/10 rounded-lg transition-colors"
                    title="删除"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Skill Form Modal */}
      {isModalOpen && (
        <SkillFormModal
          onClose={() => setIsModalOpen(false)}
          onSubmit={handleCreateSkill}
          isSubmitting={isSubmitting}
          error={submitError}
        />
      )}

      {/* Skill Edit Modal */}
      {isEditModalOpen && editingSkill && (
        <SkillEditModal
          skill={editingSkill}
          onClose={() => {
            setIsEditModalOpen(false);
            setEditingSkill(null);
          }}
          onSubmit={handleUpdateSkill}
          isSubmitting={isSubmitting}
          error={submitError}
        />
      )}
    </div>
  );
}

interface SkillFormModalProps {
  onClose: () => void;
  onSubmit: (data: Partial<SkillConfig>) => void;
  isSubmitting: boolean;
  error: string | null;
}

function SkillFormModal({ onClose, onSubmit, isSubmitting, error }: SkillFormModalProps) {
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    trigger_keywords: "",
    system_prompt: "",
    required_tools: [] as string[],
    enabled: true,
  });

  // Available tools for selection
  const availableTools = ["web_search", "web_fetch", "memory_search", "mcp_tools", "code_executor"];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // 直接传递逗号分隔的字符串，后端会自行解析
    onSubmit({
      name: formData.name,
      description: formData.description,
      trigger_keywords: formData.trigger_keywords,
      system_prompt: formData.system_prompt,
      required_tools: formData.required_tools,
      enabled: formData.enabled,
    });
  };

  const handleToolToggle = (tool: string) => {
    setFormData((prev) => ({
      ...prev,
      required_tools: prev.required_tools.includes(tool)
        ? prev.required_tools.filter((t) => t !== tool)
        : [...prev.required_tools, tool],
    }));
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />

      {/* Modal */}
      <div className="relative bg-background rounded-lg shadow-lg w-full max-w-md mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-lg font-semibold">添加 Skill</h2>
          <button
            onClick={onClose}
            className="p-1 rounded-md hover:bg-accent"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          {error && (
            <div className="p-3 bg-destructive/10 border border-destructive text-destructive rounded-lg text-sm">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium mb-2">
              名称 <span className="text-destructive">*</span>
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="请输入 Skill 名称"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">描述</label>
            <input
              type="text"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="请输入 Skill 描述"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              触发关键词 <span className="text-muted-foreground">(逗号分隔)</span>
            </label>
            <input
              type="text"
              value={formData.trigger_keywords}
              onChange={(e) => setFormData({ ...formData, trigger_keywords: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="例如: search, query, 搜索"
            />
            <p className="text-xs text-muted-foreground mt-1">
              当用户输入包含这些关键词时，将触发此 Skill
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">系统提示词</label>
            <textarea
              value={formData.system_prompt}
              onChange={(e) => setFormData({ ...formData, system_prompt: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              rows={4}
              placeholder="请输入系统提示词，定义 Skill 的行为"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">所需工具</label>
            <div className="flex flex-wrap gap-2">
              {availableTools.map((tool) => (
                <button
                  key={tool}
                  type="button"
                  onClick={() => handleToolToggle(tool)}
                  className={`px-3 py-1 text-sm rounded-full border transition-colors ${
                    formData.required_tools.includes(tool)
                      ? "bg-primary text-primary-foreground border-primary"
                      : "bg-background hover:bg-accent"
                  }`}
                >
                  {tool}
                </button>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-3">
            <input
              type="checkbox"
              id="skill-enabled"
              checked={formData.enabled}
              onChange={(e) => setFormData({ ...formData, enabled: e.target.checked })}
              className="w-4 h-4 rounded border-gray-300 text-primary focus:ring-primary"
            />
            <label htmlFor="skill-enabled" className="text-sm font-medium">
              启用
            </label>
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border rounded-lg hover:bg-accent"
            >
              取消
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50"
            >
              {isSubmitting ? "创建中..." : "创建"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

interface SkillEditModalProps {
  skill: SkillConfig;
  onClose: () => void;
  onSubmit: (data: Partial<SkillConfig>) => void;
  isSubmitting: boolean;
  error: string | null;
}

function SkillEditModal({ skill, onClose, onSubmit, isSubmitting, error }: SkillEditModalProps) {
  const [formData, setFormData] = useState({
    name: skill.name,
    description: skill.description || "",
    trigger_keywords: skill.trigger_keywords || "",
    system_prompt: skill.system_prompt || "",
    required_tools: skill.required_tools || [],
    enabled: skill.enabled,
  });

  // Available tools for selection
  const availableTools = ["web_search", "web_fetch", "memory_search", "mcp_tools", "code_executor"];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    onSubmit({
      name: formData.name,
      description: formData.description,
      trigger_keywords: formData.trigger_keywords,
      system_prompt: formData.system_prompt,
      required_tools: formData.required_tools,
      enabled: formData.enabled,
    });
  };

  const handleToolToggle = (tool: string) => {
    setFormData((prev) => ({
      ...prev,
      required_tools: prev.required_tools.includes(tool)
        ? prev.required_tools.filter((t) => t !== tool)
        : [...prev.required_tools, tool],
    }));
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />

      {/* Modal */}
      <div className="relative bg-background rounded-lg shadow-lg w-full max-w-md mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-lg font-semibold">编辑 Skill</h2>
          <button
            onClick={onClose}
            className="p-1 rounded-md hover:bg-accent"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          {error && (
            <div className="p-3 bg-destructive/10 border border-destructive text-destructive rounded-lg text-sm">
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium mb-2">
              名称 <span className="text-destructive">*</span>
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="请输入 Skill 名称"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">描述</label>
            <input
              type="text"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="请输入 Skill 描述"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              触发关键词 <span className="text-muted-foreground">(逗号分隔)</span>
            </label>
            <input
              type="text"
              value={formData.trigger_keywords}
              onChange={(e) => setFormData({ ...formData, trigger_keywords: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="例如: search, query, 搜索"
            />
            <p className="text-xs text-muted-foreground mt-1">
              当用户输入包含这些关键词时，将触发此 Skill
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">系统提示词</label>
            <textarea
              value={formData.system_prompt}
              onChange={(e) => setFormData({ ...formData, system_prompt: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              rows={4}
              placeholder="请输入系统提示词，定义 Skill 的行为"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">所需工具</label>
            <div className="flex flex-wrap gap-2">
              {availableTools.map((tool) => (
                <button
                  key={tool}
                  type="button"
                  onClick={() => handleToolToggle(tool)}
                  className={`px-3 py-1 text-sm rounded-full border transition-colors ${
                    formData.required_tools.includes(tool)
                      ? "bg-primary text-primary-foreground border-primary"
                      : "bg-background hover:bg-accent"
                  }`}
                >
                  {tool}
                </button>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-3">
            <input
              type="checkbox"
              id="edit-skill-enabled"
              checked={formData.enabled}
              onChange={(e) => setFormData({ ...formData, enabled: e.target.checked })}
              className="w-4 h-4 rounded border-gray-300 text-primary focus:ring-primary"
            />
            <label htmlFor="edit-skill-enabled" className="text-sm font-medium">
              启用
            </label>
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border rounded-lg hover:bg-accent"
            >
              取消
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50"
            >
              {isSubmitting ? "保存中..." : "保存"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
