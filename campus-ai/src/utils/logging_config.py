import sys
from loguru import logger
from ..core.config import get_settings

def setup_logging():
    """设置日志配置"""
    settings = get_settings()

    # 移除默认处理器
    logger.remove()

    # 控制台输出配置
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    logger.add(
        sys.stderr,
        format=console_format,
        level=settings.log_level,
        colorize=True,
        backtrace=True,
        diagnose=settings.debug
    )

    # 文件输出配置
    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss} | "
        "{level: <8} | "
        "{name}:{function}:{line} | "
        "{message}"
    )

    logger.add(
        "logs/app.log",
        format=file_format,
        level="DEBUG" if settings.debug else "INFO",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        backtrace=True,
        diagnose=settings.debug
    )

    # 错误日志单独文件
    logger.add(
        "logs/error.log",
        format=file_format,
        level="ERROR",
        rotation="5 MB",
        retention="90 days",
        compression="zip"
    )

    logger.info(f"✅ 日志系统初始化完成 (级别: {settings.log_level})")
    return logger