# Debug 进度记录

## 2026-03-12

### 问题描述
用户提问 "给我讲一个睡前故事" 时报错 "Request failed"。

### 排查过程

1. **检查 Docker 容器状态**
   ```bash
   docker ps
   ```
   发现 backend 容器状态为 `Restarting (3)`

2. **查看 backend 容器日志**
   ```bash
   docker logs drw_backend --tail 100
   ```
   发现关键错误：
   ```
   PermissionError: [Errno 13] Permission denied: '/logs'
   ```

3. **根因分析**
   - Logger 类在 `backend/app/utils/logger.py` 中使用 `Path(__file__).parent.parent.parent.parent / "logs"` 计算日志目录
   - 在 Docker 容器中，代码被挂载到 `/app` 目录
   - 计算路径时向上走 4 级超出了项目根目录，变成了 `/logs`
   - `/logs` 目录没有写权限，导致启动失败

4. **修复方案**
   修改 `logger.py`，增加 Docker 环境检测逻辑：

   ```python
   import os
   from pathlib import Path

   def _get_log_root_dir() -> Path:
       # 1. 检查环境变量
       if log_dir := os.environ.get("LOG_DIR"):
           return Path(log_dir)

       # 2. 检测是否在 Docker 容器中 (代码在 /app 目录下)
       app_dir = Path("/app")
       if app_dir.exists():
           return app_dir / "logs"

       # 3. 本地开发环境
       return Path(__file__).parent.parent.parent.parent / "logs"

   LOG_ROOT_DIR = _get_log_root_dir()
   ```

5. **重新构建并启动**
   ```bash
   docker-compose build backend
   docker-compose up -d backend
   ```

6. **验证结果**
   - 容器状态变为 `healthy`
   - 服务正常启动

### 附带问题
bcrypt 警告信息：
```
passlib.handlers.bcrypt | (trapped) error reading bcrypt version
AttributeError: module 'bcrypt' has no attribute '__about__'
```
这是 `passlib` 库与新版 `bcrypt` 库的兼容性问题，不影响功能，可忽略。

### 结论
问题已修复，服务恢复正常。

---

## 2026-03-12 (续)

### 问题描述
多轮对话不连续，agent 在第二轮对话时忘记之前说过什么。

### 排查过程

1. **问题分析**
   - 用户提问: "什么是雷军妙妙屋？"
   - agent 回答后，用户说: "你猜一下"
   - agent 像是完全不知道上一轮对话的内容

2. **Agent Team 调查**
   - 检查前端 chat API 调用 (frontend/src/api/chat.ts)
   - 检查前端 chat hook (frontend/src/hooks/useChat.ts)
   - 检查前端 chat store (frontend/src/stores/chatStore.ts)
   - 检查后端 chat API (backend/app/api/v1/chat.py)

3. **根因定位**
   - 后端正确返回 `X-Session-Id` 响应头
   - 前端没有读取这个 header
   - 第一条消息发送时没有 session_id，后端创建新会话并返回 session_id
   - 前端没有更新 currentSession，导致后续消息也没有带正确的 session_id
   - 后端每次都创建新会话，所以没有历史消息

### 修复方案

1. **frontend/src/api/chat.ts**
   - 在 `StreamCallback` 类型中添加 `onSessionId` 回调
   - 在收到响应时读取 `X-Session-Id` header 并触发回调

2. **frontend/src/stores/chatStore.ts**
   - 添加 `updateCurrentSessionId` 方法用于更新会话 ID

3. **frontend/src/hooks/useChat.ts**
   - 在 `onSessionId` 回调中调用 `updateCurrentSessionId` 更新会话 ID

### 验证
- 重新构建并部署 frontend Docker 容器
- 测试多轮对话是否连续

### 结论
问题已修复，多轮对话功能恢复正常。

---

## 2026-03-14

### 问题描述
Tools/Skills/MCP 配置页面存在以下问题：
1. 点击"添加工具/添加Skill/添加服务器"按钮无任何反应
2. 启用/禁用按钮点击后报错 "切换工具状态失败，请重试"
3. 编辑工具后点击保存显示 "Tool not found"

### 排查过程

#### 第一阶段：添加功能修复

1. **任务分解**
   - 使用 plan-decomposer 将任务拆分为 3 个子方案
   - 分别对应 Tools、Skills、MCP 三个配置页

2. **前端开发**
   - 调用 frontend-dev agent 添加三个页面的添加表单模态框
   - 修复后端 API 与前端数据格式不匹配问题：
     - Skills: `trigger_keywords` 应为逗号分隔字符串，不是数组
     - MCP: 字段应为顶层结构，不是嵌套 config 对象

3. **API 验证**
   - 所有 CRUD API 测试通过（使用 curl 直接测试后端）

#### 第二阶段：启用/禁用和编辑功能修复

1. **用户反馈问题**
   - 添加功能正常了，但启用/禁用和编辑功能仍然失败
   - 报错信息不明确，需要深入排查

2. **排查步骤**

   a. **直接 API 测试**
   ```bash
   # 测试 toggle API
   curl -X PATCH "http://localhost:8000/api/v1/tools/4/toggle" \
     -H "Authorization: Bearer $TOKEN" \
     -d '{"enabled":false}'
   # 返回: {"name":"test_tool_123",...} - 成功
   ```
   后端 API 正常工作，问题在前端。

   b. **检查前端代码**
   - 检查 ToolsConfig.tsx 中的 handleToggle 函数 - 看起来正确
   - 检查 API 调用参数 - 看起来正确

   c. **检查 Token 存储**
   - 发现 `authStore` 使用 `localStorage.getItem("auth-storage")` (zustand 格式)
   - 发现 `client.ts` 使用 `localStorage.getItem("token")` - **key 不匹配！**
   - 这导致 API 请求没有携带有效 token

3. **修复 Token 读取逻辑**

   **文件**: `frontend/src/api/client.ts`

   ```typescript
   // 修复前
   const token = localStorage.getItem("token");
   
   // 修复后
   let token: string | null = null;
   const authStorage = localStorage.getItem("auth-storage");
   if (authStorage) {
     try {
       const parsed = JSON.parse(authStorage);
       token = parsed?.state?.token;
     } catch (e) {
       console.error("Failed to parse auth-storage:", e);
     }
   }
   if (!token) {
     token = localStorage.getItem("token"); // 兼容旧方式
   }
   ```

4. **重新构建测试**
   - 构建前端并测试
   - 问题仍然存在

5. **深入排查 - Docker 镜像问题**
   - 发现用户访问的是 localhost:3000 (Docker 容器)
   - 检查 docker-compose.yml：前端端口映射为 `3000:80`
   - 发现旧的前端容器仍在运行，使用旧代码
   - 需要重新构建 Docker 镜像

6. **重新构建 Docker**
   ```bash
   docker-compose build frontend
   docker-compose up -d frontend
   ```

7. **再次测试 - 发现新问题**
   - 查看容器日志发现：`PATCH /api/v1/tools/0/toggle HTTP/1.1" 400`
   - 请求成功发送了（token 问题已解决）
   - 但返回 400 错误

8. **根因分析**
   - 内置工具的 ID 都是 0
   - 后端不允许 toggle 内置工具：`if tool_id == 0: raise HTTPException(400, "Cannot toggle builtin tools")`
   - 用户点击的是内置工具（显示在最前面），所以报错

9. **最终修复**
   - 在前端隐藏内置工具（ID=0）的编辑/切换/删除按钮
   - 只允许操作自定义工具

### 修复内容

| 文件 | 修改内容 |
|------|----------|
| `frontend/src/api/client.ts` | Token 读取改为从 auth-storage 获取 |
| `frontend/src/types/citation.ts` | id 类型从 string 改为 number |
| `frontend/src/api/tools.ts` | toggle/update/delete 参数类型改为 number |
| `frontend/src/api/skills.ts` | toggle/update/delete 参数类型改为 number |
| `frontend/src/api/mcp.ts` | toggle/update/delete/test 参数类型改为 number |
| `frontend/src/pages/config/ToolsConfig.tsx` | 添加 ToolFormModal、ToolEditModal，隐藏内置工具按钮 |
| `frontend/src/pages/config/SkillsConfig.tsx` | 添加 SkillFormModal、SkillEditModal |
| `frontend/src/pages/config/MCPConfig.tsx` | 添加 MCPFormModal、MCPEditModal |

### 验证结果
- [x] Docker 镜像重新构建
- [x] 前端服务在 3000 端口正常运行
- [x] Tools 自定义工具：添加、编辑、启用/禁用、删除功能正常
- [x] Skills：添加、编辑、启用/禁用、删除功能正常
- [x] MCP：添加、编辑、测试连接、启用/禁用、删除功能正常

### 结论
问题已全部修复。主要问题是：
1. Token 存储 key 不一致导致 API 请求无认证
2. Docker 镜像未重新构建导致修改未生效
3. 内置工具 ID=0 不允许操作，需在前端隐藏按钮
