# 子方案 2: Skills 配置页添加表单功能

## 目标

为 Skills 配置页 (`/config/skills`) 添加添加 Skill 的模态框表单，使"添加 Skill"按钮具有实际功能。

## 依赖

无 - 前端独立任务，使用已有的 `skillsApi.create` 方法

## 交付物

1. 修改 `/Users/xiniuyiliao/Desktop/code/DeepResearchWeb/frontend/src/pages/config/SkillsConfig.tsx`
   - 添加 SkillFormModal 组件（内联或独立文件）
   - 实现表单包含字段:
     - name (必填)
     - description (必填)
     - trigger_keywords (数组, 用逗号分隔)
     - system_prompt (文本域)
     - required_tools (多选下拉)
     - enabled (开关)
   - 添加 isModalOpen 状态管理
   - 绑定"添加 Skill"按钮的 onClick 事件
   - 提交表单后调用 skillsApi.create 并更新列表

2. 更新类型定义（如需要）:
   - 确认/扩展 `SkillConfig` 类型包含新字段

## 涉及的模块

- frontend: `pages/config/SkillsConfig.tsx`, `api/skills.ts`
- backend: 无需修改（API 已存在）

## 验收标准

- [ ] 点击"添加 Skill"按钮打开模态框
- [ ] 表单包含 name, description, trigger_keywords, system_prompt, required_tools, enabled 字段
- [ ] trigger_keywords 支持逗号分隔输入
- [ ] 提交表单后调用 POST /skills API
- [ ] 创建成功后自动关闭模态框并刷新列表
- [ ] 显示加载状态和错误提示
- [ ] 可选：支持编辑已有 Skill

---

## 详细实现指南

### 表单字段设计

```
name: string (必填, max 100 chars)
description: string (必填, max 500 chars)
trigger_keywords: string[] (从逗号分隔字符串转换)
system_prompt: string (可选, max 2000 chars)
required_tools: string[] (可选, 多选)
enabled: boolean (默认 true)
```

### 现有 API 引用

```typescript
// skillsApi.create 接口已存在
create: async (data: Omit<SkillConfig, "id">): Promise<SkillConfig>
```

### 建议的 UI 结构

```
SkillsConfig
├── isModalOpen: boolean
├── handleOpenModal(): void
├── handleCloseModal(): void
├── handleSubmit(data): Promise<void>
└── SkillFormModal (或内联表单)
    ├── name input
    ├── description textarea
    ├── trigger_keywords input (comma-separated)
    ├── system_prompt textarea
    ├── required_tools multi-select
    ├── enabled switch
    ├── submit button
    └── cancel button
```
