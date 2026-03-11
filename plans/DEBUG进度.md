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
