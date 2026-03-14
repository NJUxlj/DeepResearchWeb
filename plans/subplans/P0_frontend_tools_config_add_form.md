# 子方案 1: Tools 配置页添加表单功能

## 目标

为 Tools 配置页 (`/config/tools`) 添加添加工具的模态框表单，使"添加工具"按钮具有实际功能。

## 依赖

无 - 前端独立任务，使用已有的 `toolsApi.create` 方法

## 交付物

1. 修改 `/Users/xiniuyiliao/Desktop/code/DeepResearchWeb/frontend/src/pages/config/ToolsConfig.tsx`
   - 添加 ToolFormModal 组件（内联或独立文件）
   - 实现表单包含字段: name (必填), description (必填), tool_type (下拉选择), config (JSON 编辑器), enabled (开关)
   - 添加 isModalOpen 状态管理
   - 绑定"添加工具"按钮的 onClick 事件
   - 提交表单后调用 toolsApi.create 并更新列表

2. 更新类型定义（如需要）:
   - 确认 `ToolConfig` 类型包含 `tool_type` 字段

## 涉及的模块

- frontend: `pages/config/ToolsConfig.tsx`, `api/tools.ts`
- backend: 无需修改（API 已存在）

## 验收标准

- [ ] 点击"添加工具"按钮打开模态框
- [ ] 表单包含 name, description, tool_type, config, enabled 字段
- [ ] 提交表单后调用 POST /tools API
- [ ] 创建成功后自动关闭模态框并刷新列表
- [ ] 显示加载状态和错误提示
- [ ] 可选：支持编辑已有工具

---

## 详细实现指南

### 表单字段设计

```
name: string (必填, max 100 chars)
description: string (必填, max 500 chars)
tool_type: enum ['function', 'mcp', 'custom'] (必填)
config: object (可选, JSON 编辑器)
enabled: boolean (默认 true)
```

### 现有 API 引用

```typescript
// toolsApi.create 接口已存在
create: async (data: Omit<ToolConfig, "id">): Promise<ToolConfig>
```

### 建议的 UI 结构

```
ToolsConfig
├── isModalOpen: boolean
├── handleOpenModal(): void
├── handleCloseModal(): void
├── handleSubmit(data): Promise<void>
└── ToolFormModal (或内联表单)
    ├── name input
    ├── description textarea
    ├── tool_type select
    ├── config json editor
    ├── enabled switch
    ├── submit button
    └── cancel button
```
