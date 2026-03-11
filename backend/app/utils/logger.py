"""Logger utility for DeepResearchWeb."""

import os
from datetime import datetime
from pathlib import Path
from typing import Literal

# 确定日志根目录
# 优先级: 环境变量 > Docker 容器 > 本地开发
def _get_log_root_dir() -> Path:
    # 1. 检查环境变量
    if log_dir := os.environ.get("LOG_DIR"):
        return Path(log_dir)

    # 2. 检测是否在 Docker 容器中 (代码在 /app 目录下)
    app_dir = Path("/app")
    if app_dir.exists():
        # Docker 环境，使用 /app/logs
        return app_dir / "logs"

    # 3. 本地开发环境，使用项目根目录的 logs
    # 从 utils/logger.py 向上走 4 级到项目根目录
    return Path(__file__).parent.parent.parent.parent / "logs"

LOG_ROOT_DIR = _get_log_root_dir()

# 确保日志目录存在
LOG_ROOT_DIR.mkdir(parents=True, exist_ok=True)


class Logger:
    """Logger 类，用于将日志写入指定文件。

    Usage:
        logger = Logger("my_module")
        logger.log("This is an info message")
        logger.log("This is a warning", mode="warning")
        logger.log("This is an error", mode="error")
    """

    def __init__(self, name: str):
        """初始化 Logger。

        Args:
            name: 日志文件名（不含扩展名），会自动添加 .log 后缀
        """
        self.name = name
        self.log_file = LOG_ROOT_DIR / f"{name}.log"

    def log(
        self,
        message: str,
        mode: Literal["info", "warning", "error"] = "info",
    ) -> None:
        """写入日志。

        Args:
            message: 日志内容
            mode: 日志级别，可选 "info", "warning", "error"，默认为 "info"
        """
        # 验证 mode
        if mode not in ["info", "warning", "error"]:
            mode = "info"

        # 构建日志行
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [{mode.upper()}] {message}\n"

        # 写入文件
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_line)


# 便捷函数：创建默认 Logger
def get_logger(name: str) -> Logger:
    """获取 Logger 实例的便捷函数。

    Args:
        name: 日志文件名

    Returns:
        Logger 实例
    """
    return Logger(name)
