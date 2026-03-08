import { useState, useEffect } from "react";
import { Zap, Plus, Trash2, Power, PowerOff } from "lucide-react";
import { skillsApi } from "@/api/skills";
import type { SkillConfig } from "@/types/citation";

export function SkillsConfig() {
  const [skills, setSkills] = useState<SkillConfig[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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

  const handleToggle = async (id: string, enabled: boolean) => {
    try {
      await skillsApi.toggle(id, !enabled);
      setSkills((prev) =>
        prev.map((skill) =>
          skill.id === id ? { ...skill, enabled: !enabled } : skill
        )
      );
    } catch (err) {
      console.error("Failed to toggle skill:", err);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("确定要删除这个 Skill 吗？")) return;
    try {
      await skillsApi.delete(id);
      setSkills((prev) => prev.filter((skill) => skill.id !== id));
    } catch (err) {
      console.error("Failed to delete skill:", err);
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
        <button className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90">
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
    </div>
  );
}
