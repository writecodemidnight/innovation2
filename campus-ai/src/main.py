from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from .core.config import get_settings
from .core.lifespan import lifespan
from .core.monitoring import setup_monitoring
from .api.health import router as health_router
from .api.v1 import api_v1_router

try:
    from .api.v3 import v3_router
    V3_AVAILABLE = True
except ImportError:
    V3_AVAILABLE = False

from .utils.logging_config import setup_logging

# 获取配置
settings = get_settings()

# 初始化日志配置
setup_logging()

# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="校园社团活动评估系统 - 算法服务",
    openapi_url=f"{settings.api_prefix}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 设置监控
metrics = setup_monitoring(app)

# 注册路由
app.include_router(health_router, tags=["健康检查"])
app.include_router(api_v1_router, prefix=settings.api_prefix, tags=["算法接口"])

# 注册V3路由（如果可用）
if V3_AVAILABLE:
    app.include_router(v3_router)
    logger.info("✅ V3 API路由已注册")

@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info(f"🚀 {settings.app_name} v{settings.app_version} 启动成功")
    logger.info(f"📊 API文档地址: http://localhost:8000/docs")
    logger.info(f"📈 监控指标地址: http://localhost:8000/metrics")
    logger.info(f"📝 日志级别: {settings.log_level}")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info(f"🛑 {settings.app_name} 正在关闭...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )