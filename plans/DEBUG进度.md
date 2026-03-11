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
