"""Logger utility for DeepResearchWeb."""

from datetime import datetime
from pathlib import Path
from typing import Literal

# 日志根目录（使用相对路径，基于项目根目录）
LOG_ROOT_DIR = Path(__file__).parent.parent.parent.parent / "logs"

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
