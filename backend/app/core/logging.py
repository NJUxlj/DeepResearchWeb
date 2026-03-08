"""结构化日志配置."""

import logging
import sys
from logging.handlers import RotatingFileHandler

from app.config import settings


def setup_logging() -> None:
    """配置应用日志."""

    # 日志级别
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    # 根日志配置
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # 清除现有的处理器
    root_logger.handlers.clear()

    # 控制台处理器 - 人类可读格式
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # 控制台日志格式
    console_format = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(console_format)
    root_logger.addHandler(console_handler)

    # 文件日志处理器
    try:
        file_handler = RotatingFileHandler(
            filename="logs/app.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(console_format)
        root_logger.addHandler(file_handler)
    except Exception:
        # 如果无法创建文件日志，仅使用控制台
        pass

    # 设置第三方库的日志级别
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """获取指定名称的日志记录器."""
    return logging.getLogger(name)


# 预配置的日志记录器
logger = get_logger("app")
