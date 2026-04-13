from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from loguru import logger

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """应用生命周期管理：启动预热和优雅关闭"""
    logger.info("🚀 算法服务启动中...")

    # 应用启动逻辑
    try:
        # 初始化关键组件
        from .config import get_settings
        settings = get_settings()

        # 初始化模型管理器（将在后续任务实现）
        app.state.settings = settings

        logger.info(f"✅ 算法服务启动完成 (环境: {'开发' if settings.debug else '生产'})")

        yield  # 应用运行期

    finally:
        # 应用关闭逻辑
        logger.info("🛑 算法服务关闭中...")

        # 清理资源
        if hasattr(app.state, 'model_manager'):
            try:
                await app.state.model_manager.cleanup()
                logger.info("✅ 模型管理器清理完成")
            except Exception as e:
                logger.error(f"❌ 模型管理器清理失败: {e}")

        logger.info("👋 算法服务已关闭")