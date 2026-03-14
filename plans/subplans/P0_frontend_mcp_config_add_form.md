# 子方案 3: MCP 配置页添加表单功能

## 目标

为 MCP 配置页 (`/config/mcp`) 添加添加 MCP 服务器的模态框表单，使"添加服务器"按钮具有实际功能。

## 依赖

无 - 前端独立任务，使用已有的 `mcpApi.create` 方法

## 交付物

1. 修改 `/Users/xiniuyiliao/Desktop/code/DeepResearchWeb/frontend/src/pages/config/MCPConfig.tsx`
   - 添加 MCPFormModal 组件（内联或独立文件）
   - 实现表单包含字段:
     - name (必填)
     - description (可选)
     - transport (单选: stdio / http)
     - command (当 transport=stdio 时必填)
     - args (当 transport=stdio 时可选, 数组)
     - env (当 transport=stdio 时可选, key-value 对)
     - url (当 transport=http 时必填)
     - enabled (开关)
   - 添加 isModalOpen 状态管理
   - 绑定"添加服务器"按钮的 onClick 事件
   - 提交表单后调用 mcpApi.create 并更新列表
   - transport 切换时动态显示/隐藏相应字段

2. 更新类型定义（如需要）:
   - 确认 `MCPConfig` 类型正确匹配后端

## 涉及的模块

- frontend: `pages/config/MCPConfig.tsx`, `api/mcp.ts`
- backend: 无需修改（API 已存在）

## 验收标准

- [ ] 点击"添加服务器"按钮打开模态框
- [ ] 表单包含 name, description, transport, command/args/env/url, enabled 字段
- [ ] transport 切换时动态显示对应配置字段 (stdio: command/args/env, http: url)
- [ ] 提交表单后调用 POST /mcp/servers API
- [ ] 创建成功后自动关闭模态框并刷新列表
- [ ] 显示加载状态和错误提示
- [ ] 可选：支持编辑已有 MCP 服务器

---

## 详细实现指南

### 表单字段设计

```
name: string (必填, max 100 chars)
description: string (可选, max 500 chars)
transport: enum ['stdio', 'http'] (必填, 默认 stdio)

--- 当 transport = 'stdio' 时 ---
command: string (必填)
args: string[] (可选, 每行一个或逗号分隔)
env: Record<string, string> (可选, key-value 对)

--- 当 transport = 'http' 时 ---
url: string (必填, valid URL)

enabled: boolean (默认 true)
```

### 现有 API 引用

```typescript
// mcpApi.create 接口已存在
create: async (data: Omit<MCPConfig, "id">): Promise<MCPConfig>
```

### 建议的 UI 结构

```
MCPConfig
├── isModalOpen: boolean
├── handleOpenModal(): void
├── handleCloseModal(): void
├── handleSubmit(data): Promise<void>
└── MCPFormModal (或内联表单)
    ├── name input
    ├── description textarea
    ├── transport radio (stdio/http)
    ├── conditional fields:
    │   ├── command input (stdio)
    │   ├── args input (stdio)
    │   ├── env key-value (stdio)
    │   └── url input (http)
    ├── enabled switch
    ├── submit button
    └── cancel button
```

### 动态字段显示逻辑

```typescript
const [transport, setTransport] = useState<'stdio' | 'http'>('stdio');

// 渲染条件字段
{transport === 'stdio' && (
  <>
    <input name="command" required />
    <input name="args" />
    <envEditor />
  </>
)}

{transport === 'http' && (
  <input name="url" required type="url" />
)}
```
