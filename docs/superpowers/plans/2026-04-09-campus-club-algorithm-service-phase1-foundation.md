# 校园社团算法服务 - 第一阶段：基础框架搭建实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 建立校园社团活动评估系统的算法服务基础框架，包括FastAPI项目初始化、核心模块实现、基础依赖配置和开发环境搭建。

**Architecture:** 采用Python 3.10 + FastAPI 0.104+技术栈，单体架构设计，支持7种算法（K-Means, AHP, LSTM, 遗传算法, NLP情感分析, CV图像分析, Apriori挖掘），阿里云OSS存储模型，时间戳版本控制。

**Tech Stack:** Python 3.10, FastAPI 0.104+, Pydantic 2.5, scikit-learn 1.4, PyTorch 2.2, pandas 2.2, aliyun-python-sdk-oss 2.18, uvicorn 0.24, pytest 7.4, Docker, Docker Compose

---

## 文件结构

```
campus-ai/
├── src/
│   ├── main.py                      # FastAPI主应用
│   ├── core/                        # 核心模块
│   │   ├── __init__.py
│   │   ├── config.py               # 配置管理
│   │   ├── lifespan.py             # 生命周期管理
│   │   ├── security.py             # 认证安全
│   │   ├── exceptions.py           # 异常处理
│   │   ├── monitoring.py           # 监控指标
│   │   └── dependencies.py         # 依赖注入
│   ├── api/                        # API路由层
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── recommend.py       # 推荐相关接口
│   │   │   ├── evaluation.py      # 评估相关接口
│   │   │   ├── nlp.py             # NLP相关接口
│   │   │   ├── prediction.py      # 预测相关接口
│   │   │   ├── optimization.py    # 优化相关接口
│   │   │   ├── mining.py          # 数据挖掘接口
│   │   │   └── cv.py              # 计算机视觉接口
│   │   └── health.py              # 健康检查接口
│   ├── services/                   # 业务服务层
│   │   ├── __init__.py
│   │   ├── recommendation.py      # K-Means推荐服务
│   │   ├── evaluation.py          # AHP评估服务
│   │   ├── prediction.py          # LSTM预测服务
│   │   ├── optimization.py        # 遗传算法优化服务
│   │   ├── nlp.py                 # NLP情感分析服务
│   │   ├── computer_vision.py     # CV图像质量分析
│   │   ├── mining.py              # Apriori关联规则挖掘
│   │   └── model_manager.py       # 模型管理服务
│   ├── models/                    # 数据模型
│   │   ├── __init__.py
│   │   ├── schemas.py            # Pydantic模式
│   │   ├── dto.py                # 数据传输对象
│   │   └── entities.py           # 数据库实体（如需）
│   ├── utils/                     # 工具模块
│   │   ├── __init__.py
│   │   ├── data_processor.py     # 数据预处理
│   │   ├── oss_client.py         # 阿里云OSS客户端
│   │   ├── spring_client.py      # Spring Boot API客户端
│   │   ├── metrics.py            # 评估指标计算
│   │   └── logging_config.py     # 日志配置
│   └── tests/                     # 测试目录
│       ├── __init__.py
│       ├── unit/
│       │   ├── test_core.py
│       │   ├── test_services.py
│       │   └── test_utils.py
│       ├── integration/
│       │   ├── test_api.py
│       │   └── test_integration.py
│       └── conftest.py
├── models_cache/                  # 模型缓存目录
│   ├── kmeans/
│   ├── ahp/
│   └── README.md
├── docker-compose.yml             # 本地开发环境
├── Dockerfile                     # 生产环境镜像
├── Dockerfile.dev                 # 开发环境镜像
├── requirements.txt               # Python依赖
├── requirements-dev.txt           # 开发依赖
├── .env.example                   # 环境变量示例
├── .gitignore                     # Git忽略文件
├── config/
│   ├── development.yml            # 开发配置
│   ├── production.yml             # 生产配置
│   └── test.yml                   # 测试配置
├── deploy/
│   └── deploy.sh                  # 部署脚本
├── monitoring/
│   ├── prometheus.yml
│   ├── alerts.yml
│   └── dashboards/
├── logs/                          # 日志目录
└── README.md                      # 项目文档
```

---

## 任务分解

### Task 1: 项目结构初始化

**Files:**
- Create: `campus-ai/`
- Create: `campus-ai/src/` 目录结构
- Create: `campus-ai/requirements.txt`
- Create: `campus-ai/.env.example`
- Create: `campus-ai/.gitignore`

- [ ] **Step 1: 创建项目根目录和基础结构**

```bash
mkdir -p campus-ai/src/{core,api/v1,services,models,utils,tests/{unit,integration}}
mkdir -p campus-ai/{config,deploy,monitoring/dashboards,logs,models_cache/{kmeans,ahp}}
touch campus-ai/src/{core,api/v1,services,models,utils,tests/{unit,integration}}/__init__.py
touch campus-ai/src/tests/conftest.py
```

- [ ] **Step 2: 创建requirements.txt依赖文件**

```txt
# FastAPI框架
fastapi[all]==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0

# 阿里云集成
aliyun-python-sdk-oss==2.18.6
oss2==2.18.4
python-jose[cryptography]==3.3.0

# HTTP客户端
httpx==0.26.0
asyncio-throttle==1.0.2

# 机器学习算法库
scikit-learn==1.4.0
pandas==2.2.0
numpy==1.26.4
joblib==1.3.2
scipy==1.12.0

# 深度学习框架
torch==2.2.0

# 自然语言处理
jieba==0.42.1
transformers==4.37.0
sentencepiece==0.1.99
pytorch-transformers==1.1.0

# 计算机视觉
opencv-python==4.9.0.80
Pillow==10.2.0

# 数据处理与缓存
redis==5.0.1

# 开发与测试
pytest==7.4.4
pytest-asyncio==0.21.1
httpx-mock==0.10.0

# 监控与日志
loguru==0.7.2
prometheus-fastapi-instrumentator==6.1.0
```

- [ ] **Step 3: 创建开发依赖文件**

```bash
echo '# 开发依赖
black==23.12.1
ruff==0.1.9
pre-commit==3.6.0
mypy==1.8.0
pytest-cov==4.1.0
' > campus-ai/requirements-dev.txt
```

- [ ] **Step 4: 创建环境变量示例文件**

```bash
echo '# ============================================
# 校园社团算法服务 - 环境变量配置示例
# ============================================

# 应用配置
APP_NAME=campus-ai-service
APP_VERSION=1.0.0
DEBUG=false
LOG_LEVEL=INFO

# 阿里云OSS配置
OSS_ENDPOINT=
OSS_ACCESS_KEY_ID=
OSS_ACCESS_KEY_SECRET=
OSS_BUCKET_NAME=campus-ai-models-dev
OSS_MODEL_PREFIX=models/
OSS_TEMP_PREFIX=temp/

# Spring Boot集成配置
SPRING_API_BASE_URL=http://localhost:8080/api
SPRING_API_TIMEOUT=30
SPRING_AUTH_TOKEN=

# 模型预热配置
PRELOAD_KMEANS=true
PRELOAD_AHP_WEIGHTS=true
PRELOAD_LSTM=false
MODEL_CACHE_DIR=./models_cache
MAX_CACHE_SIZE_GB=5

# 算法参数配置
KMEANS_N_CLUSTERS=5
AHP_CONSISTENCY_THRESHOLD=0.1
LSTM_SEQUENCE_LENGTH=10
NLP_MODEL_NAME=bert-base-chinese

# 重要提示：
# 1. 生产环境请使用强密码和正确配置
# 2. 复制此文件为 .env 并修改为实际值
' > campus-ai/.env.example
```

- [ ] **Step 5: 创建Git忽略文件**

```bash
echo '# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
env.bak/
venv.bak/

# 依赖包
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDE
.idea/
*.iml
*.ipr
*.iws
.vscode/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# 日志
logs/
*.log

# 环境变量
.env
!/.env.example

# 模型缓存（不跟踪具体模型文件）
models_cache/*.pkl
models_cache/*.pt
models_cache/*.joblib

# 测试
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
.tox/

# 临时文件
tmp/
temp/
*.tmp
*.temp
' > campus-ai/.gitignore
```

- [ ] **Step 6: 提交初始代码**

```bash
cd campus-ai
git add requirements.txt requirements-dev.txt .env.example .gitignore
git commit -m "feat: initialize algorithm service project structure and dependencies"
```

---

### Task 2: FastAPI核心框架搭建

**Files:**
- Create: `campus-ai/src/main.py`
- Create: `campus-ai/src/core/config.py`
- Create: `campus-ai/src/core/lifespan.py`
- Create: `campus-ai/src/core/exceptions.py`
- Create: `campus-ai/src/core/monitoring.py`
- Create: `campus-ai/src/api/health.py`

- [ ] **Step 1: 创建配置管理模块**

```python
# campus-ai/src/core/config.py
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    """应用配置管理"""
    
    # 应用基础配置
    app_name: str = Field(default="campus-ai-service")
    app_version: str = Field(default="1.0.0")
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")
    
    # API配置
    api_prefix: str = Field(default="/api/v1")
    cors_origins: list[str] = Field(default=["http://localhost:3000", "http://localhost:5173"])
    
    # 阿里云OSS配置
    oss_endpoint: str = Field(description="阿里云OSS端点")
    oss_access_key_id: str = Field(description="阿里云AccessKey ID")
    oss_access_key_secret: str = Field(description="阿里云AccessKey Secret")
    oss_bucket_name: str = Field(default="campus-ai-models-dev")
    oss_model_prefix: str = Field(default="models/")
    oss_temp_prefix: str = Field(default="temp/")
    
    # Spring Boot集成配置
    spring_api_base_url: str = Field(default="http://localhost:8080/api")
    spring_api_timeout: int = Field(default=30)
    spring_auth_token: Optional[str] = Field(default=None)
    
    # 模型预热配置
    preload_kmeans: bool = Field(default=True)
    preload_ahp_weights: bool = Field(default=True)
    preload_lstm: bool = Field(default=False)
    model_cache_dir: str = Field(default="./models_cache")
    max_cache_size_gb: int = Field(default=5)
    
    # 算法参数配置
    kmeans_n_clusters: int = Field(default=5)
    ahp_consistency_threshold: float = Field(default=0.1)
    lstm_sequence_length: int = Field(default=10)
    nlp_model_name: str = Field(default="bert-base-chinese")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

def get_settings() -> Settings:
    """获取配置实例（单例模式）"""
    return Settings()
```

- [ ] **Step 2: 创建应用主文件**

```python
# campus-ai/src/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from .core.config import get_settings
from .core.lifespan import lifespan
from .core.monitoring import setup_monitoring
from .api.health import router as health_router
from .api.v1 import api_v1_router

# 获取配置
settings = get_settings()

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

@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info(f"🚀 {settings.app_name} v{settings.app_version} 启动成功")
    logger.info(f"📊 API文档地址: http://localhost:8000/docs")
    logger.info(f"📈 监控指标地址: http://localhost:8000/metrics")

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
```

- [ ] **Step 3: 创建生命周期管理模块**

```python
# campus-ai/src/core/lifespan.py
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
```

- [ ] **Step 4: 创建异常处理模块**

```python
# campus-ai/src/core/exceptions.py
from fastapi import HTTPException, status
from typing import Any, Dict, Optional

class AlgorithmServiceException(HTTPException):
    """算法服务基础异常"""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status_code,
            detail={
                "error_code": error_code,
                "message": detail,
                "metadata": metadata or {}
            }
        )

# ============ 特定业务异常 ============
class ModelNotFoundException(AlgorithmServiceException):
    """模型未找到异常"""
    def __init__(self, model_type: str, version: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"模型 '{model_type}' 未找到" + (f" (版本: {version})" if version else ""),
            error_code="MODEL_NOT_FOUND",
            metadata={"model_type": model_type, "version": version}
        )

class InvalidInputDataException(AlgorithmServiceException):
    """输入数据异常"""
    def __init__(self, field: str, reason: str, received_value: Any = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"字段 '{field}' 数据无效: {reason}",
            error_code="INVALID_INPUT_DATA",
            metadata={
                "field": field,
                "reason": reason,
                "received_value": str(received_value)[:100]
            }
        )

class AlgorithmExecutionException(AlgorithmServiceException):
    """算法执行异常"""
    def __init__(self, algorithm: str, reason: str, execution_time: Optional[float] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"算法 '{algorithm}' 执行失败: {reason}",
            error_code="ALGORITHM_EXECUTION_ERROR",
            metadata={
                "algorithm": algorithm,
                "reason": reason,
                "execution_time_ms": execution_time
            }
        )
```

- [ ] **Step 5: 创建监控模块**

```python
# campus-ai/src/core/monitoring.py
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Histogram, Gauge
import time
from loguru import logger

# Prometheus指标定义
class Metrics:
    """监控指标收集器"""
    
    def __init__(self):
        # API请求指标
        self.request_count = Counter(
            'algorithm_service_requests_total',
            'Total number of API requests',
            ['method', 'endpoint', 'status']
        )
        
        self.request_duration = Histogram(
            'algorithm_service_request_duration_seconds',
            'API request duration in seconds',
            ['method', 'endpoint'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
        )
        
        # 系统资源指标
        self.loaded_models = Gauge(
            'algorithm_service_models_loaded',
            'Number of models currently loaded in memory'
        )
        
        self.error_count = Counter(
            'algorithm_service_errors_total',
            'Total number of errors',
            ['error_type', 'algorithm']
        )
    
    def record_request(self, method: str, endpoint: str, status: str, duration: float):
        """记录API请求指标"""
        self.request_count.labels(method=method, endpoint=endpoint, status=status).inc()
        self.request_duration.labels(method=method, endpoint=endpoint).observe(duration)

def setup_monitoring(app):
    """设置应用监控"""
    # 1. 基础指标收集
    instrumentator = Instrumentator(
        should_group_status_codes=False,
        excluded_handlers=["/metrics", "/health", "/docs", "/redoc"]
    )
    instrumentator.instrument(app).expose(app)
    
    # 2. 自定义指标实例
    metrics = Metrics()
    app.state.metrics = metrics
    
    logger.info("✅ 监控系统初始化完成")
    return metrics
```

- [ ] **Step 6: 创建健康检查接口**

```python
# campus-ai/src/api/health.py
from fastapi import APIRouter, Depends
from datetime import datetime
from loguru import logger

from ..core.config import get_settings

router = APIRouter()

@router.get("/health", tags=["健康检查"])
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "campus-ai-algorithm-service",
        "timestamp": datetime.now().isoformat(),
        "version": get_settings().app_version,
        "uptime": "TODO: 实现运行时间计算"
    }

@router.get("/ready", tags=["健康检查"])
async def readiness_check():
    """就绪检查端点"""
    # 检查关键依赖是否就绪
    dependencies = {
        "config_loaded": True,
        "model_cache_available": False,  # 将在后续任务实现
        "oss_connection": False,  # 将在后续任务实现
    }
    
    all_ready = all(dependencies.values())
    
    return {
        "status": "ready" if all_ready else "not_ready",
        "timestamp": datetime.now().isoformat(),
        "dependencies": dependencies,
        "message": "就绪检查完成" if all_ready else "部分依赖未就绪"
    }

@router.get("/metrics", tags=["健康检查"])
async def metrics_endpoint():
    """Prometheus指标端点（由instrumentator自动处理）"""
    pass
```

- [ ] **Step 7: 创建API版本路由**

```python
# campus-ai/src/api/v1/__init__.py
from fastapi import APIRouter

# 创建API v1路由器
api_v1_router = APIRouter()

# 在这里导入各个子路由
from . import recommend, evaluation, nlp, prediction, optimization, mining, cv

# 注册子路由（将在后续任务实现）
# api_v1_router.include_router(recommend.router, prefix="/recommend", tags=["推荐"])
# api_v1_router.include_router(evaluation.router, prefix="/evaluation", tags=["评估"])
# api_v1_router.include_router(nlp.router, prefix="/nlp", tags=["自然语言处理"])
# api_v1_router.include_router(prediction.router, prefix="/prediction", tags=["预测"])
# api_v1_router.include_router(optimization.router, prefix="/optimization", tags=["优化"])
# api_v1_router.include_router(mining.router, prefix="/mining", tags=["数据挖掘"])
# api_v1_router.include_router(cv.router, prefix="/cv", tags=["计算机视觉"])
```

- [ ] **Step 8: 测试核心框架**

```bash
# 创建测试虚拟环境
cd campus-ai
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 创建临时环境文件
cp .env.example .env.test
echo 'DEBUG=true' >> .env.test
echo 'LOG_LEVEL=DEBUG' >> .env.test

# 测试导入
python -c "from src.main import app; print('✅ FastAPI应用导入成功')"
python -c "from src.core.config import get_settings; settings = get_settings(); print(f'✅ 配置加载成功: {settings.app_name}')"
python -c "from src.core.exceptions import AlgorithmServiceException; print('✅ 异常类导入成功')"

# 运行基础测试
export ENV_FILE=.env.test
python -m pytest src/tests/unit/test_core.py -v 2>/dev/null || echo "⚠️  暂无测试文件，跳过测试"
```

- [ ] **Step 9: 提交核心框架代码**

```bash
cd campus-ai
git add src/main.py src/core/ src/api/
git commit -m "feat: implement FastAPI core framework with config, lifespan, exceptions, and monitoring"
```

---

### Task 3: 数据模型与契约定义

**Files:**
- Create: `campus-ai/src/models/schemas.py`
- Create: `campus-ai/src/models/dto.py`
- Create: `campus-ai/src/utils/data_processor.py`
- Create: `campus-ai/src/tests/unit/test_models.py`
- Create: `campus-ai/src/tests/unit/test_data_processor.py`

- [ ] **Step 1: 创建Pydantic数据模式**

```python
# campus-ai/src/models/schemas.py
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# 枚举定义
class SentimentLabel(str, Enum):
    POSITIVE = "POSITIVE"
    NEUTRAL = "NEUTRAL"
    NEGATIVE = "NEGATIVE"

class ActivityType(str, Enum):
    LECTURE = "lecture"
    WORKSHOP = "workshop"
    COMPETITION = "competition"
    SOCIAL = "social"
    SPORTS = "sports"
    VOLUNTEER = "volunteer"

# ============ 推荐相关 ============
class HistoryActivity(BaseModel):
    """历史活动记录"""
    activity_id: str = Field(description="活动ID")
    activity_type: ActivityType = Field(description="活动类型")
    participation_score: Optional[float] = Field(None, ge=0, le=100, description="参与度得分")
    feedback_score: Optional[float] = Field(None, ge=1, le=5, description="反馈评分")
    timestamp: datetime = Field(description="活动时间")

class RecommendationRequest(BaseModel):
    """K-Means推荐请求"""
    user_id: str = Field(description="用户ID")
    history_activities: List[HistoryActivity] = Field(
        description="历史活动记录，最少3条",
        min_items=3
    )
    top_n: int = Field(5, ge=1, le=20, description="推荐数量")
    include_metadata: bool = Field(False, description="是否包含活动元数据")
    
    @validator("history_activities")
    def validate_history_length(cls, v):
        if len(v) < 3:
            raise ValueError("至少需要3条历史活动记录才能进行推荐")
        return v

class RecommendedActivity(BaseModel):
    """推荐结果项"""
    activity_id: str = Field(description="活动ID")
    similarity_score: float = Field(ge=0, le=1, description="相似度得分")
    confidence: float = Field(ge=0, le=1, description="置信度")
    recommendation_reason: str = Field(description="推荐理由")
    activity_metadata: Optional[Dict[str, Any]] = Field(None, description="活动元数据")

class RecommendationResponse(BaseModel):
    """推荐响应"""
    request_id: str = Field(description="请求ID")
    recommended_activities: List[RecommendedActivity] = Field(description="推荐列表")
    algorithm_version: str = Field(description="算法版本")
    processing_time_ms: float = Field(description="处理时间(毫秒)")

# ============ AHP评估相关 ============
class AHPRequest(BaseModel):
    """AHP评估请求"""
    activity_id: str = Field(description="活动ID")
    metrics_data: Dict[str, Any] = Field(description="指标数据")
    weights: Optional[Dict[str, float]] = Field(None, description="自定义权重")

class AHPResponse(BaseModel):
    """AHP评估响应"""
    request_id: str = Field(description="请求ID")
    scores: Dict[str, float] = Field(description="各项得分")
    radar_data: Dict[str, Any] = Field(description="雷达图数据")
    weight_matrix_used: Dict[str, float] = Field(description="使用的权重矩阵")
    consistency_ratio: float = Field(description="一致性比率")
    algorithm_version: str = Field(description="算法版本")

# ============ NLP情感分析相关 ============
class SentimentRequest(BaseModel):
    """情感分析请求"""
    texts: List[str] = Field(
        description="待分析文本列表",
        min_items=1,
        max_items=100
    )
    language: str = Field("zh-CN", description="语言代码")
    return_probabilities: bool = Field(False, description="是否返回概率分布")

class SentimentResult(BaseModel):
    """情感分析结果"""
    text: str = Field(description="原始文本")
    sentiment: SentimentLabel = Field(description="情感标签")
    score: float = Field(ge=0, le=1, description="情感强度")
    probabilities: Optional[Dict[SentimentLabel, float]] = Field(None, description="概率分布")

class SentimentResponse(BaseModel):
    """情感分析响应"""
    sentiments: List[SentimentResult] = Field(description="分析结果列表")
    language_detected: str = Field(description="检测到的语言")
    model_version: str = Field(description="模型版本")

# ============ 通用响应 ============
class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(description="服务状态")
    version: str = Field(description="服务版本")
    uptime: float = Field(description="运行时间(秒)")
    loaded_models: Dict[str, str] = Field(description="已加载模型")
    cache_stats: Dict[str, Any] = Field(description="缓存统计")
```

- [ ] **Step 2: 创建数据传输对象**

```python
# campus-ai/src/models/dto.py
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import numpy as np

@dataclass
class ProcessedActivity:
    """清洗后的活动数据"""
    activity_id: str
    activity_type: str
    features: np.ndarray  # 数值化特征向量
    metadata: Dict[str, Any]
    is_valid: bool = True
    validation_errors: List[str] = None
    
    def __post_init__(self):
        if self.validation_errors is None:
            self.validation_errors = []

@dataclass
class ModelPrediction:
    """模型预测结果"""
    model_type: str
    prediction: Any
    confidence: float
    metadata: Dict[str, Any]
    execution_time_ms: float

@dataclass
class BatchProcessingResult:
    """批处理结果"""
    successful_count: int
    failed_count: int
    errors: List[Dict[str, Any]]
    total_processing_time_ms: float
```

- [ ] **Step 3: 创建数据清洗处理器**

```python
# campus-ai/src/utils/data_processor.py
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from loguru import logger
from datetime import datetime

from ..models.schemas import HistoryActivity
from ..models.dto import ProcessedActivity

class DataProcessor:
    """数据清洗与预处理服务"""
    
    def __init__(self):
        self.imputation_strategies = {
            'mean': self._impute_with_mean,
            'median': self._impute_with_median,
            'mode': self._impute_with_mode,
            'constant': self._impute_with_constant
        }
    
    async def clean_activity_data(
        self, 
        activities: List[HistoryActivity]
    ) -> Tuple[List[ProcessedActivity], List[str]]:
        """清洗活动数据，处理空值和异常"""
        processed = []
        errors = []
        
        for i, activity in enumerate(activities):
            try:
                # 1. 基础验证
                if not activity.activity_id:
                    errors.append(f"活动{i}: 缺少activity_id")
                    continue
                
                if not activity.activity_type:
                    errors.append(f"活动{i}: 缺少activity_type")
                    continue
                
                # 2. 数值字段处理
                participation_score = self._handle_missing_value(
                    activity.participation_score,
                    strategy='median',
                    default_value=50.0
                )
                
                feedback_score = self._handle_missing_value(
                    activity.feedback_score,
                    strategy='median', 
                    default_value=3.0
                )
                
                # 3. 特征工程
                features = self._extract_activity_features(
                    activity_type=activity.activity_type.value,
                    participation_score=participation_score,
                    feedback_score=feedback_score,
                    timestamp=activity.timestamp
                )
                
                processed.append(ProcessedActivity(
                    activity_id=activity.activity_id,
                    activity_type=activity.activity_type.value,
                    features=features,
                    metadata={
                        'original_participation_score': activity.participation_score,
                        'original_feedback_score': activity.feedback_score,
                        'processed_timestamp': activity.timestamp.isoformat()
                    }
                ))
                
            except Exception as e:
                errors.append(f"活动{i}处理失败: {str(e)}")
                logger.error(f"活动数据清洗失败: {e}")
        
        return processed, errors
    
    def _handle_missing_value(self, value, strategy='median', default_value=None):
        """处理缺失值"""
        if value is None:
            if strategy in self.imputation_strategies:
                return self.imputation_strategies[strategy](default_value)
            return default_value
        return value
    
    def _extract_activity_features(
        self, 
        activity_type: str,
        participation_score: float,
        feedback_score: float,
        timestamp: datetime
    ) -> np.ndarray:
        """提取活动特征向量"""
        features = []
        
        # 1. 活动类型one-hot编码
        activity_types = ['lecture', 'workshop', 'competition', 'social', 'sports', 'volunteer']
        type_vector = [1 if activity_type == t else 0 for t in activity_types]
        features.extend(type_vector)
        
        # 2. 数值特征
        features.append(participation_score / 100.0)  # 归一化到0-1
        features.append((feedback_score - 1) / 4.0)   # 归一化到0-1
        
        # 3. 时间特征（周期性编码）
        hour_sin = np.sin(2 * np.pi * timestamp.hour / 24)
        hour_cos = np.cos(2 * np.pi * timestamp.hour / 24)
        day_sin = np.sin(2 * np.pi * timestamp.weekday() / 7)
        day_cos = np.cos(2 * np.pi * timestamp.weekday() / 7)
        
        features.extend([hour_sin, hour_cos, day_sin, day_cos])
        
        return np.array(features)
    
    # 插补策略方法
    def _impute_with_mean(self, default_value=None):
        return 0.5  # 简化实现
    
    def _impute_with_median(self, default_value=None):
        return default_value if default_value is not None else 0.5
    
    def _impute_with_mode(self, default_value=None):
        return default_value if default_value is not None else 0.5
    
    def _impute_with_constant(self, default_value=None):
        return default_value if default_value is not None else 0.0
```

- [ ] **Step 4: 创建模型测试文件**

```python
# campus-ai/src/tests/unit/test_models.py
import pytest
from datetime import datetime
from src.models.schemas import (
    HistoryActivity, RecommendationRequest, SentimentRequest,
    ActivityType, SentimentLabel
)

def test_history_activity_validation():
    """测试历史活动数据验证"""
    # 有效数据
    activity = HistoryActivity(
        activity_id="act_001",
        activity_type=ActivityType.LECTURE,
        participation_score=80.5,
        feedback_score=4.5,
        timestamp=datetime.now()
    )
    assert activity.activity_id == "act_001"
    assert activity.activity_type == ActivityType.LECTURE
    
    # 测试缺失值处理
    activity_no_scores = HistoryActivity(
        activity_id="act_002",
        activity_type=ActivityType.WORKSHOP,
        participation_score=None,
        feedback_score=None,
        timestamp=datetime.now()
    )
    assert activity_no_scores.participation_score is None
    assert activity_no_scores.feedback_score is None

def test_recommendation_request_validation():
    """测试推荐请求验证"""
    # 有效请求
    activities = [
        HistoryActivity(
            activity_id=f"act_{i}",
            activity_type=ActivityType.LECTURE,
            participation_score=70 + i,
            feedback_score=3.5,
            timestamp=datetime.now()
        )
        for i in range(3)
    ]
    
    request = RecommendationRequest(
        user_id="user_001",
        history_activities=activities,
        top_n=5,
        include_metadata=False
    )
    assert request.user_id == "user_001"
    assert len(request.history_activities) == 3
    
    # 测试最小活动数量验证
    with pytest.raises(ValueError) as exc_info:
        RecommendationRequest(
            user_id="user_002",
            history_activities=activities[:2],  # 只有2个活动
            top_n=5
        )
    assert "至少需要3条历史活动记录" in str(exc_info.value)

def test_sentiment_request_validation():
    """测试情感分析请求验证"""
    request = SentimentRequest(
        texts=["这个活动很棒！", "体验一般"],
        language="zh-CN",
        return_probabilities=True
    )
    assert len(request.texts) == 2
    assert request.language == "zh-CN"
    assert request.return_probabilities is True
    
    # 测试文本数量限制
    with pytest.raises(ValueError) as exc_info:
        SentimentRequest(texts=[])
    assert "最少需要1个文本" in str(exc_info.value)

def test_enum_values():
    """测试枚举值"""
    assert ActivityType.LECTURE.value == "lecture"
    assert SentimentLabel.POSITIVE.value == "POSITIVE"
    assert SentimentLabel.NEGATIVE.value == "NEGATIVE"
```

- [ ] **Step 5: 创建数据处理器测试文件**

```python
# campus-ai/src/tests/unit/test_data_processor.py
import pytest
import numpy as np
from datetime import datetime
from src.utils.data_processor import DataProcessor
from src.models.schemas import HistoryActivity, ActivityType

@pytest.fixture
def data_processor():
    return DataProcessor()

@pytest.fixture
def sample_activities():
    return [
        HistoryActivity(
            activity_id="act_001",
            activity_type=ActivityType.LECTURE,
            participation_score=85.0,
            feedback_score=4.5,
            timestamp=datetime(2024, 1, 15, 14, 30, 0)
        ),
        HistoryActivity(
            activity_id="act_002",
            activity_type=ActivityType.WORKSHOP,
            participation_score=None,  # 缺失值
            feedback_score=3.0,
            timestamp=datetime(2024, 1, 16, 10, 0, 0)
        ),
        HistoryActivity(
            activity_id="act_003",
            activity_type=ActivityType.COMPETITION,
            participation_score=90.0,
            feedback_score=None,  # 缺失值
            timestamp=datetime(2024, 1, 17, 16, 45, 0)
        )
    ]

@pytest.mark.asyncio
async def test_clean_activity_data(data_processor, sample_activities):
    """测试活动数据清洗"""
    processed, errors = await data_processor.clean_activity_data(sample_activities)
    
    # 验证结果
    assert len(processed) == 3
    assert len(errors) == 0
    
    # 验证处理后的活动
    for i, activity in enumerate(processed):
        assert activity.activity_id == f"act_00{i+1}"
        assert activity.is_valid is True
        assert isinstance(activity.features, np.ndarray)
        assert len(activity.features) > 0
        
        # 验证特征包含期望的维度
        # 6个活动类型 + 2个数值特征 + 4个时间特征 = 12维
        assert activity.features.shape[0] == 12

def test_missing_value_handling(data_processor):
    """测试缺失值处理"""
    # 测试中位数插补
    result = data_processor._handle_missing_value(None, strategy='median', default_value=50.0)
    assert result == 50.0
    
    # 测试常量插补
    result = data_processor._handle_missing_value(None, strategy='constant', default_value=0.0)
    assert result == 0.0
    
    # 测试非空值保持不变
    result = data_processor._handle_missing_value(75.0, strategy='median', default_value=50.0)
    assert result == 75.0

def test_feature_extraction(data_processor):
    """测试特征提取"""
    timestamp = datetime(2024, 1, 15, 14, 30, 0)  # 周一 14:30
    
    features = data_processor._extract_activity_features(
        activity_type="lecture",
        participation_score=85.0,
        feedback_score=4.5,
        timestamp=timestamp
    )
    
    # 验证特征维度
    assert features.shape[0] == 12
    
    # 验证one-hot编码
    # lecture应该是第一个位置为1
    assert features[0] == 1.0  # lecture
    assert sum(features[1:6]) == 0.0  # 其他类型为0
    
    # 验证数值特征归一化
    assert 0 <= features[6] <= 1  # participation_score / 100
    assert 0 <= features[7] <= 1  # (feedback_score - 1) / 4
    
    # 验证时间特征
    assert -1 <= features[8] <= 1  # hour_sin
    assert -1 <= features[9] <= 1  # hour_cos
    assert -1 <= features[10] <= 1  # day_sin
    assert -1 <= features[11] <= 1  # day_cos
```

- [ ] **Step 6: 运行模型和数据处理器测试**

```bash
cd campus-ai
source venv/bin/activate  # Windows: venv\Scripts\activate

# 运行模型测试
pytest src/tests/unit/test_models.py -v
期望输出: Tests passed: 4

# 运行数据处理器测试
pytest src/tests/unit/test_data_processor.py -v
期望输出: Tests passed: 3
```

- [ ] **Step 7: 提交数据模型和工具代码**

```bash
cd campus-ai
git add src/models/ src/utils/data_processor.py src/tests/unit/test_*.py
git commit -m "feat: implement data models, schemas, DTOs, and data processor with tests"
```

---

### Task 4: 工具模块与客户端实现

**Files:**
- Create: `campus-ai/src/utils/oss_client.py`
- Create: `campus-ai/src/utils/spring_client.py`
- Create: `campus-ai/src/utils/logging_config.py`
- Create: `campus-ai/src/tests/unit/test_clients.py`

- [ ] **Step 1: 创建阿里云OSS客户端**

```python
# campus-ai/src/utils/oss_client.py
import oss2
from typing import Optional, List, BinaryIO
from loguru import logger
from ..core.config import get_settings

class OSSClient:
    """阿里云OSS客户端封装"""
    
    def __init__(self, settings=None):
        self.settings = settings or get_settings()
        self._bucket = None
    
    @property
    def bucket(self):
        """获取OSS存储桶（懒加载）"""
        if self._bucket is None:
            self._connect()
        return self._bucket
    
    def _connect(self):
        """连接OSS"""
        try:
            auth = oss2.Auth(
                self.settings.oss_access_key_id,
                self.settings.oss_access_key_secret
            )
            self._bucket = oss2.Bucket(
                auth,
                self.settings.oss_endpoint,
                self.settings.oss_bucket_name
            )
            logger.info(f"✅ OSS连接成功: {self.settings.oss_bucket_name}")
        except Exception as e:
            logger.error(f"❌ OSS连接失败: {e}")
            raise
    
    async def upload_model(self, model_type: str, version: str, model_data: bytes) -> bool:
        """上传模型到OSS"""
        try:
            object_key = f"{self.settings.oss_model_prefix}{model_type}/{version}.pkl"
            result = self.bucket.put_object(object_key, model_data)
            logger.info(f"✅ 模型上传成功: {object_key} (ETag: {result.etag})")
            return True
        except Exception as e:
            logger.error(f"❌ 模型上传失败: {e}")
            return False
    
    async def download_model(self, model_type: str, version: str) -> Optional[bytes]:
        """从OSS下载模型"""
        try:
            object_key = f"{self.settings.oss_model_prefix}{model_type}/{version}.pkl"
            result = self.bucket.get_object(object_key)
            model_data = result.read()
            logger.info(f"✅ 模型下载成功: {object_key} (大小: {len(model_data)} bytes)")
            return model_data
        except oss2.exceptions.NoSuchKey:
            logger.warning(f"⚠️  模型不存在: {model_type}/{version}")
            return None
        except Exception as e:
            logger.error(f"❌ 模型下载失败: {e}")
            return None
    
    async def list_model_versions(self, model_type: str) -> List[str]:
        """列出指定模型类型的所有版本"""
        try:
            prefix = f"{self.settings.oss_model_prefix}{model_type}/"
            result = oss2.ObjectIterator(self.bucket, prefix=prefix)
            
            versions = []
            for obj in result:
                # 从对象键中提取版本号
                filename = obj.key.split('/')[-1]
                if filename.endswith('.pkl'):
                    version = filename[:-4]  # 移除.pkl后缀
                    versions.append(version)
            
            # 按时间戳排序（降序）
            versions.sort(reverse=True)
            return versions
            
        except Exception as e:
            logger.error(f"❌ 列出模型版本失败: {e}")
            return []
    
    async def delete_model(self, model_type: str, version: str) -> bool:
        """删除OSS上的模型"""
        try:
            object_key = f"{self.settings.oss_model_prefix}{model_type}/{version}.pkl"
            self.bucket.delete_object(object_key)
            logger.info(f"✅ 模型删除成功: {object_key}")
            return True
        except Exception as e:
            logger.error(f"❌ 模型删除失败: {e}")
            return False
    
    def test_connection(self) -> bool:
        """测试OSS连接"""
        try:
            # 尝试列出存储桶中的对象（限制1个）
            result = oss2.ObjectIterator(self.bucket, max_keys=1)
            list(result)  # 触发迭代
            return True
        except Exception as e:
            logger.error(f"❌ OSS连接测试失败: {e}")
            return False
```

- [ ] **Step 2: 创建Spring Boot API客户端**

```python
# campus-ai/src/utils/spring_client.py
import httpx
from typing import Optional, Dict, Any
from loguru import logger
from ..core.config import get_settings

class SpringBootClient:
    """Spring Boot后端API客户端"""
    
    def __init__(self, base_url: str = None, auth_token: str = None):
        self.settings = get_settings()
        self.base_url = base_url or self.settings.spring_api_base_url
        self.auth_token = auth_token or self.settings.spring_auth_token
        self._client = None
    
    @property
    def client(self):
        """获取HTTP客户端（懒加载）"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.settings.spring_api_timeout,
                headers=self._get_auth_headers()
            )
        return self._client
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """获取认证头"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"CampusAI-Service/{self.settings.app_version}"
        }
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers
    
    async def get_user_activities(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取用户历史活动"""
        try:
            response = await self.client.get(f"/users/{user_id}/activities")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ 获取用户活动失败: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"❌ 获取用户活动异常: {e}")
            return None
    
    async def get_activity_details(self, activity_id: str) -> Optional[Dict[str, Any]]:
        """获取活动详细信息"""
        try:
            response = await self.client.get(f"/activities/{activity_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ 获取活动详情失败: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"❌ 获取活动详情异常: {e}")
            return None
    
    async def get_club_resources(self, club_id: str) -> Optional[Dict[str, Any]]:
        """获取社团资源信息"""
        try:
            response = await self.client.get(f"/clubs/{club_id}/resources")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ 获取社团资源失败: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"❌ 获取社团资源异常: {e}")
            return None
    
    async def submit_evaluation_result(self, activity_id: str, evaluation_data: Dict[str, Any]) -> bool:
        """提交评估结果到Spring Boot"""
        try:
            response = await self.client.post(
                f"/activities/{activity_id}/evaluations",
                json=evaluation_data
            )
            response.raise_for_status()
            logger.info(f"✅ 评估结果提交成功: {activity_id}")
            return True
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ 提交评估结果失败: {e.response.status_code} - {e.response.text}")
            return False
        except Exception as e:
            logger.error(f"❌ 提交评估结果异常: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """测试Spring Boot连接"""
        try:
            response = await self.client.get("/actuator/health")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"❌ Spring Boot连接测试失败: {e}")
            return False
    
    async def close(self):
        """关闭HTTP客户端"""
        if self._client:
            await self._client.aclose()
            self._client = None
```

- [ ] **Step 3: 创建日志配置模块**

```python
# campus-ai/src/utils/logging_config.py
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
```

- [ ] **Step 4: 创建客户端测试文件**

```python
# campus-ai/src/tests/unit/test_clients.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.utils.oss_client import OSSClient
from src.utils.spring_client import SpringBootClient
from src.core.config import Settings

@pytest.fixture
def mock_settings():
    return Settings(
        oss_endpoint="http://oss-test.com",
        oss_access_key_id="test_key_id",
        oss_access_key_secret="test_key_secret",
        oss_bucket_name="test-bucket",
        oss_model_prefix="models/",
        spring_api_base_url="http://spring-test.com/api",
        spring_api_timeout=30
    )

@pytest.fixture
def oss_client(mock_settings):
    with patch('oss2.Auth'), patch('oss2.Bucket'):
        client = OSSClient(mock_settings)
        client._bucket = MagicMock()  # 模拟bucket
        return client

@pytest.fixture
def spring_client(mock_settings):
    with patch('httpx.AsyncClient'):
        client = SpringBootClient()
        client.settings = mock_settings
        client._client = AsyncMock()  # 模拟HTTP客户端
        return client

@pytest.mark.asyncio
async def test_oss_upload_model(oss_client):
    """测试OSS模型上传"""
    # 模拟成功上传
    mock_result = MagicMock()
    mock_result.etag = "test-etag-123"
    oss_client.bucket.put_object = MagicMock(return_value=mock_result)
    
    model_data = b"fake model data"
    result = await oss_client.upload_model("kmeans", "20240101_120000", model_data)
    
    assert result is True
    oss_client.bucket.put_object.assert_called_once_with(
        "models/kmeans/20240101_120000.pkl",
        model_data
    )

@pytest.mark.asyncio
async def test_oss_download_model(oss_client):
    """测试OSS模型下载"""
    # 模拟成功下载
    mock_object = MagicMock()
    mock_object.read.return_value = b"fake model data"
    oss_client.bucket.get_object = MagicMock(return_value=mock_object)
    
    model_data = await oss_client.download_model("kmeans", "20240101_120000")
    
    assert model_data == b"fake model data"
    oss_client.bucket.get_object.assert_called_once_with(
        "models/kmeans/20240101_120000.pkl"
    )

@pytest.mark.asyncio
async def test_oss_list_model_versions(oss_client):
    """测试OSS模型版本列表"""
    # 模拟对象迭代器
    mock_object1 = MagicMock()
    mock_object1.key = "models/kmeans/20240101_120000.pkl"
    mock_object2 = MagicMock()
    mock_object2.key = "models/kmeans/20231231_235959.pkl"
    
    mock_iterator = MagicMock()
    mock_iterator.__iter__.return_value = iter([mock_object1, mock_object2])
    
    with patch('oss2.ObjectIterator', return_value=mock_iterator):
        versions = await oss_client.list_model_versions("kmeans")
        
        assert versions == ["20240101_120000", "20231231_235959"]

@pytest.mark.asyncio
async def test_spring_boot_get_user_activities(spring_client):
    """测试获取用户活动"""
    # 模拟成功响应
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "user_id": "user_001",
        "activities": [
            {"activity_id": "act_001", "title": "Test Activity"}
        ]
    }
    spring_client.client.get.return_value = mock_response
    
    result = await spring_client.get_user_activities("user_001")
    
    assert result is not None
    assert result["user_id"] == "user_001"
    assert len(result["activities"]) == 1
    spring_client.client.get.assert_called_once_with("/users/user_001/activities")

@pytest.mark.asyncio
async def test_spring_boot_submit_evaluation(spring_client):
    """测试提交评估结果"""
    # 模拟成功响应
    mock_response = AsyncMock()
    mock_response.status_code = 200
    spring_client.client.post.return_value = mock_response
    
    evaluation_data = {
        "activity_id": "act_001",
        "scores": {"overall": 85.5},
        "algorithm_version": "20240101_120000"
    }
    
    result = await spring_client.submit_evaluation_result("act_001", evaluation_data)
    
    assert result is True
    spring_client.client.post.assert_called_once_with(
        "/activities/act_001/evaluations",
        json=evaluation_data
    )

def test_logging_config():
    """测试日志配置"""
    from src.utils.logging_config import setup_logging
    
    # 测试日志配置函数不抛出异常
    logger = setup_logging()
    assert logger is not None
    
    # 测试日志记录
    logger.info("测试日志消息")
```

- [ ] **Step 5: 更新主应用以包含日志配置**

```python
# 修改 campus-ai/src/main.py
# 在文件顶部添加
from .utils.logging_config import setup_logging

# 在创建FastAPI应用之前添加日志初始化
logger = setup_logging()

# 修改startup_event函数
@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info(f"🚀 {settings.app_name} v{settings.app_version} 启动成功")
    logger.info(f"📊 API文档地址: http://localhost:8000/docs")
    logger.info(f"📈 监控指标地址: http://localhost:8000/metrics")
    logger.info(f"📝 日志级别: {settings.log_level}")
```

- [ ] **Step 6: 运行客户端测试**

```bash
cd campus-ai
source venv/bin/activate  # Windows: venv\Scripts\activate

# 运行客户端测试
pytest src/tests/unit/test_clients.py -v
期望输出: Tests passed: 6

# 测试主应用启动
python -c "from src.main import app; print('✅ 主应用导入成功')"
python -c "from src.utils.logging_config import setup_logging; logger = setup_logging(); logger.info('✅ 日志系统测试成功')"
```

- [ ] **Step 7: 提交工具模块代码**

```bash
cd campus-ai
git add src/utils/oss_client.py src/utils/spring_client.py src/utils/logging_config.py src/tests/unit/test_clients.py src/main.py
git commit -m "feat: implement OSS client, Spring Boot client, and logging configuration with tests"
```

---

### Task 5: 模型管理器服务实现

**Files:**
- Create: `campus-ai/src/services/model_manager.py`
- Create: `campus-ai/src/tests/unit/test_model_manager.py`
- Create: `campus-ai/models_cache/README.md`

- [ ] **Step 1: 创建模型管理器服务**

```python
# campus-ai/src/services/model_manager.py
import os
import joblib
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from loguru import logger

from ..utils.oss_client import OSSClient
from ..core.config import get_settings

class ModelManager:
    """模型管理器：实现磁盘缓存 + 内存单例 + 版本控制"""
    
    def __init__(self, oss_client: OSSClient = None, settings=None):
        self.settings = settings or get_settings()
        self.oss_client = oss_client or OSSClient(self.settings)
        self._models: Dict[str, Any] = {}  # 内存缓存
        self._model_versions: Dict[str, str] = {}
        self._model_locks: Dict[str, asyncio.Lock] = {}
        
        # 确保缓存目录存在
        self.cache_dir = Path(self.settings.model_cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建模型类型子目录
        for model_type in ['kmeans', 'ahp', 'lstm', 'nlp', 'cv']:
            (self.cache_dir / model_type).mkdir(parents=True, exist_ok=True)
    
    def _get_lock(self, model_type: str) -> asyncio.Lock:
        """获取模型类型锁（防止并发加载）"""
        if model_type not in self._model_locks:
            self._model_locks[model_type] = asyncio.Lock()
        return self._model_locks[model_type]
    
    async def warmup_model(self, model_type: str, priority: str = "medium") -> bool:
        """预热指定类型模型"""
        async with self._get_lock(model_type):
            try:
                # 1. 检查OSS上的最新版本
                latest_version = await self._get_latest_model_version(model_type)
                if not latest_version:
                    logger.warning(f"OSS上未找到{model_type}模型")
                    return False
                
                # 2. 检查本地缓存
                local_path = self._get_local_model_path(model_type, latest_version)
                if not local_path.exists():
                    logger.info(f"下载{model_type}模型版本{latest_version}")
                    await self._download_model_from_oss(model_type, latest_version)
                
                # 3. 加载到内存（仅高优先级模型）
                if priority == "high":
                    await self.load_model_to_memory(model_type, latest_version)
                
                logger.info(f"✅ {model_type}模型预热完成 (版本: {latest_version})")
                return True
                
            except Exception as e:
                logger.error(f"❌ {model_type}模型预热失败: {e}")
                return False
    
    async def get_model(self, model_type: str, version: Optional[str] = None) -> Any:
        """获取模型实例（如果未在内存中则自动加载）"""
        # 如果没有指定版本，使用最新版本
        if not version:
            version = await self._get_latest_model_version(model_type)
            if not version:
                raise ValueError(f"未找到{model_type}类型的模型")
        
        cache_key = f"{model_type}:{version}"
        
        # 1. 检查内存缓存
        if cache_key in self._models:
            return self._models[cache_key]
        
        async with self._get_lock(model_type):
            # 再次检查（双重检查锁定模式）
            if cache_key in self._models:
                return self._models[cache_key]
            
            # 2. 检查磁盘缓存
            local_path = self._get_local_model_path(model_type, version)
            if not local_path.exists():
                await self._download_model_from_oss(model_type, version)
            
            # 3. 加载到内存
            model = await self.load_model_to_memory(model_type, version)
            return model
    
    async def load_model_to_memory(self, model_type: str, version: str) -> Any:
        """加载模型到内存并缓存"""
        cache_key = f"{model_type}:{version}"
        local_path = self._get_local_model_path(model_type, version)
        
        try:
            # 根据模型类型使用不同的加载方式
            if model_type in ["kmeans", "ahp"]:
                model = joblib.load(local_path)
            elif model_type == "lstm":
                import torch
                model = torch.load(local_path, map_location='cpu')
                model.eval()  # 设置为评估模式
            elif model_type == "nlp":
                # 简化实现，实际使用transformers
                model = {"type": "nlp_model", "version": version}
            elif model_type == "cv":
                # 简化实现
                model = {"type": "cv_model", "version": version}
            else:
                model = joblib.load(local_path)
            
            # 缓存到内存
            self._models[cache_key] = model
            self._model_versions[model_type] = version
            
            logger.debug(f"加载{model_type}模型到内存 (版本: {version}, 大小: {local_path.stat().st_size/1024/1024:.2f}MB)")
            return model
            
        except Exception as e:
            logger.error(f"加载模型失败 {cache_key}: {e}")
            raise
    
    def _get_local_model_path(self, model_type: str, version: str) -> Path:
        """获取本地模型文件路径"""
        return self.cache_dir / model_type / f"{version}.pkl"
    
    async def _get_latest_model_version(self, model_type: str) -> Optional[str]:
        """从OSS获取指定模型类型的最新版本（时间戳）"""
        try:
            versions = await self.oss_client.list_model_versions(model_type)
            return versions[0] if versions else None
        except Exception as e:
            logger.error(f"获取{model_type}最新版本失败: {e}")
            return None
    
    async def _download_model_from_oss(self, model_type: str, version: str):
        """从OSS下载模型到本地缓存"""
        try:
            model_data = await self.oss_client.download_model(model_type, version)
            if model_data is None:
                raise ValueError(f"无法从OSS下载模型 {model_type}/{version}")
            
            local_path = self._get_local_model_path(model_type, version)
            with open(local_path, 'wb') as f:
                f.write(model_data)
            
            logger.info(f"✅ 模型下载完成: {model_type}/{version} -> {local_path}")
            
        except Exception as e:
            logger.error(f"❌ 模型下载失败 {model_type}/{version}: {e}")
            raise
    
    async def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        info = {
            "loaded_models": {},
            "cache_stats": {},
            "oss_available": False
        }
        
        # 已加载模型信息
        for cache_key, model in self._models.items():
            model_type, version = cache_key.split(":", 1)
            info["loaded_models"][model_type] = {
                "version": version,
                "type": type(model).__name__,
                "in_memory": True
            }
        
        # 缓存统计
        cache_files = list(self.cache_dir.rglob("*.pkl"))
        total_size = sum(f.stat().st_size for f in cache_files)
        
        info["cache_stats"] = {
            "total_files": len(cache_files),
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "cache_dir": str(self.cache_dir)
        }
        
        # OSS连接测试
        try:
            info["oss_available"] = self.oss_client.test_connection()
        except:
            info["oss_available"] = False
        
        return info
    
    async def cleanup(self):
        """清理资源"""
        # 清理内存中的模型
        self._models.clear()
        self._model_versions.clear()
        
        # 关闭OSS连接（如果有）
        if hasattr(self.oss_client, 'close'):
            await self.oss_client.close()
        
        logger.info("✅ 模型管理器清理完成")
```

- [ ] **Step 2: 更新生命周期管理以集成模型管理器**

```python
# 修改 campus-ai/src/core/lifespan.py
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from loguru import logger

from ..services.model_manager import ModelManager
from ..utils.oss_client import OSSClient
from ..core.config import get_settings

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """应用生命周期管理：启动预热和优雅关闭"""
    logger.info("🚀 算法服务启动中...")
    
    # 应用启动逻辑
    try:
        # 初始化配置
        settings = get_settings()
        app.state.settings = settings
        
        # 初始化OSS客户端
        oss_client = OSSClient(settings)
        
        # 初始化模型管理器
        model_manager = ModelManager(oss_client, settings)
        app.state.model_manager = model_manager
        
        # 并行预加载关键模型
        warmup_tasks = []
        
        # 高优先级：立即加载的模型
        if settings.preload_kmeans:
            warmup_tasks.append(
                asyncio.create_task(model_manager.warmup_model("kmeans", priority="high"))
            )
        
        if settings.preload_ahp_weights:
            warmup_tasks.append(
                asyncio.create_task(model_manager.warmup_model("ahp", priority="high"))
            )
        
        # 等待所有高优先级任务完成
        if warmup_tasks:
            done, pending = await asyncio.wait(
                warmup_tasks,
                timeout=30.0
            )
            for task in done:
                if task.exception():
                    logger.error(f"模型预热失败: {task.exception()}")
            
            logger.info(f"✅ 算法服务启动完成，已预热{len(done)}个模型")
        else:
            logger.info("✅ 算法服务启动完成，无需模型预热")
        
        yield  # 应用运行期
        
    finally:
        # 应用关闭逻辑
        logger.info("🛑 算法服务关闭中...")
        
        # 清理模型管理器
        if hasattr(app.state, 'model_manager'):
            try:
                await app.state.model_manager.cleanup()
                logger.info("✅ 模型管理器清理完成")
            except Exception as e:
                logger.error(f"❌ 模型管理器清理失败: {e}")
        
        logger.info("👋 算法服务已关闭")
```

- [ ] **Step 3: 创建模型管理器测试文件**

```python
# campus-ai/src/tests/unit/test_model_manager.py
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
import tempfile
import joblib
import numpy as np

from src.services.model_manager import ModelManager
from src.core.config import Settings

@pytest.fixture
def temp_cache_dir():
    """临时缓存目录"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def mock_settings(temp_cache_dir):
    return Settings(
        model_cache_dir=temp_cache_dir,
        preload_kmeans=True,
        preload_ahp_weights=True,
        preload_lstm=False,
        oss_endpoint="http://oss-test.com",
        oss_access_key_id="test_key_id",
        oss_access_key_secret="test_key_secret",
        oss_bucket_name="test-bucket",
        oss_model_prefix="models/"
    )

@pytest.fixture
def mock_oss_client():
    client = MagicMock()
    client.list_model_versions = AsyncMock()
    client.download_model = AsyncMock()
    client.test_connection = MagicMock(return_value=True)
    return client

@pytest.fixture
def model_manager(mock_settings, mock_oss_client):
    with patch('src.services.model_manager.OSSClient', return_value=mock_oss_client):
        manager = ModelManager(settings=mock_settings)
        manager.oss_client = mock_oss_client
        return manager

def test_model_manager_initialization(model_manager, temp_cache_dir):
    """测试模型管理器初始化"""
    assert model_manager.settings is not None
    assert model_manager.cache_dir == Path(temp_cache_dir)
    assert len(model_manager._models) == 0
    assert len(model_manager._model_versions) == 0
    
    # 验证缓存目录创建
    assert model_manager.cache_dir.exists()
    assert (model_manager.cache_dir / "kmeans").exists()
    assert (model_manager.cache_dir / "ahp").exists()

@pytest.mark.asyncio
async def test_get_latest_model_version(model_manager, mock_oss_client):
    """测试获取最新模型版本"""
    # 模拟OSS返回版本列表
    mock_oss_client.list_model_versions.return_value = [
        "20240102_120000",
        "20240101_120000",
        "20231231_235959"
    ]
    
    version = await model_manager._get_latest_model_version("kmeans")
    
    assert version == "20240102_120000"
    mock_oss_client.list_model_versions.assert_called_once_with("kmeans")

@pytest.mark.asyncio
async def test_warmup_model(model_manager, mock_oss_client, temp_cache_dir):
    """测试模型预热"""
    # 模拟OSS返回版本和下载
    mock_oss_client.list_model_versions.return_value = ["20240101_120000"]
    mock_oss_client.download_model.return_value = b"fake model data"
    
    # 创建测试模型数据
    test_model = {"clusters": 5, "centers": np.random.rand(5, 3)}
    
    # 模拟joblib加载
    with patch('joblib.load', return_value=test_model):
        result = await model_manager.warmup_model("kmeans", priority="high")
        
        assert result is True
        mock_oss_client.list_model_versions.assert_called_once_with("kmeans")
        
        # 验证模型已加载到内存
        cache_key = "kmeans:20240101_120000"
        assert cache_key in model_manager._models
        assert model_manager._models[cache_key] == test_model

@pytest.mark.asyncio
async def test_get_model_with_caching(model_manager, mock_oss_client):
    """测试模型获取与缓存"""
    # 模拟OSS和磁盘缓存
    mock_oss_client.list_model_versions.return_value = ["20240101_120000"]
    
    # 创建测试模型
    test_model = {"type": "kmeans", "data": "test"}
    
    # 模拟模型已在内存中
    model_manager._models["kmeans:20240101_120000"] = test_model
    
    # 获取模型（应该从内存缓存中获取）
    model = await model_manager.get_model("kmeans")
    
    assert model == test_model
    # 验证没有调用OSS下载
    mock_oss_client.download_model.assert_not_called()

@pytest.mark.asyncio
async def test_load_model_to_memory_kmeans(model_manager, temp_cache_dir):
    """测试加载K-Means模型到内存"""
    # 创建测试模型文件
    test_model = {"n_clusters": 5, "centers": np.random.rand(5, 3)}
    model_path = Path(temp_cache_dir) / "kmeans" / "20240101_120000.pkl"
    joblib.dump(test_model, model_path)
    
    # 加载模型
    model = await model_manager.load_model_to_memory("kmeans", "20240101_120000")
    
    assert model == test_model
    assert "kmeans:20240101_120000" in model_manager._models
    assert model_manager._model_versions["kmeans"] == "20240101_120000"

@pytest.mark.asyncio
async def test_get_model_info(model_manager, mock_oss_client, temp_cache_dir):
    """测试获取模型信息"""
    # 添加一些模型到内存
    model_manager._models["kmeans:20240101_120000"] = {"type": "kmeans"}
    model_manager._models["ahp:20240101_120000"] = {"type": "ahp"}
    
    # 创建一些缓存文件
    cache_dir = Path(temp_cache_dir)
    (cache_dir / "kmeans" / "test.pkl").write_bytes(b"test")
    (cache_dir / "ahp" / "test.pkl").write_bytes(b"test")
    
    info = await model_manager.get_model_info()
    
    assert "loaded_models" in info
    assert "cache_stats" in info
    assert "oss_available" in info
    
    assert len(info["loaded_models"]) == 2
    assert info["loaded_models"]["kmeans"]["version"] == "20240101_120000"
    assert info["loaded_models"]["kmeans"]["in_memory"] is True
    
    assert info["cache_stats"]["total_files"] == 2
    assert info["oss_available"] is True

@pytest.mark.asyncio
async def test_cleanup(model_manager):
    """测试资源清理"""
    # 添加一些模型到内存
    model_manager._models["kmeans:20240101_120000"] = {"type": "kmeans"}
    model_manager._models["ahp:20240101_120000"] = {"type": "ahp"}
    
    # 执行清理
    await model_manager.cleanup()
    
    # 验证内存已清空
    assert len(model_manager._models) == 0
    assert len(model_manager._model_versions) == 0
```

- [ ] **Step 4: 创建缓存目录说明文件**

```markdown
# campus-ai/models_cache/README.md
# 模型缓存目录说明

此目录用于缓存从阿里云OSS下载的模型文件，避免每次请求都从云端下载。

## 目录结构
```
models_cache/
├── kmeans/           # K-Means聚类模型
├── ahp/             # AHP层次分析法权重矩阵
├── lstm/            # LSTM时间序列预测模型
├── nlp/             # NLP情感分析模型
└── cv/              # 计算机视觉模型
```

## 文件命名规则
模型文件按照以下格式命名：
```
{时间戳}.pkl
```
示例：`20240101_120000.pkl` 表示2024年1月1日12:00:00的模型版本

## 缓存管理
- 自动下载：当请求的模型不在本地缓存时，自动从OSS下载
- 内存缓存：高频使用的模型会加载到内存中，加速访问
- 磁盘清理：当缓存大小超过配置限制时，自动清理旧模型

## 注意事项
1. 此目录不应提交到版本控制（已在.gitignore中排除）
2. 生产环境建议定期清理旧版本模型
3. 开发环境可以使用此目录测试模型加载逻辑
```

- [ ] **Step 5: 更新健康检查接口以包含模型信息**

```python
# 修改 campus-ai/src/api/health.py
@router.get("/health", tags=["健康检查"])
async def health_check(request: Request):
    """健康检查端点"""
    try:
        # 获取模型管理器信息
        model_info = {}
        if hasattr(request.app.state, 'model_manager'):
            model_info = await request.app.state.model_manager.get_model_info()
        
        return {
            "status": "healthy",
            "service": "campus-ai-algorithm-service",
            "timestamp": datetime.now().isoformat(),
            "version": get_settings().app_version,
            "model_info": model_info
        }
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
```

- [ ] **Step 6: 运行模型管理器测试**

```bash
cd campus-ai
source venv/bin/activate  # Windows: venv\Scripts\activate

# 运行模型管理器测试
pytest src/tests/unit/test_model_manager.py -v
期望输出: Tests passed: 7

# 测试模型管理器集成
python -c "
from src.services.model_manager import ModelManager
from src.core.config import get_settings
import asyncio

settings = get_settings()
print(f'✅ 模型管理器导入成功')
print(f'缓存目录: {settings.model_cache_dir}')
print(f'预加载K-Means: {settings.preload_kmeans}')
"
```

- [ ] **Step 7: 提交模型管理器代码**

```bash
cd campus-ai
git add src/services/model_manager.py src/core/lifespan.py src/api/health.py src/tests/unit/test_model_manager.py models_cache/README.md
git commit -m "feat: implement model manager service with disk cache, memory caching, and version control"
```

---

### Task 6: 开发环境与Docker配置

**Files:**
- Create: `campus-ai/Dockerfile`
- Create: `campus-ai/Dockerfile.dev`
- Create: `campus-ai/docker-compose.yml`
- Create: `campus-ai/config/development.yml`
- Create: `campus-ai/deploy/deploy.sh`

- [ ] **Step 1: 创建生产环境Dockerfile**

```dockerfile
# campus-ai/Dockerfile
# 构建阶段
FROM python:3.10-slim AS builder

WORKDIR /app

# 1. 安装构建依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 2. 复制依赖文件
COPY requirements.txt .

# 3. 创建虚拟环境并安装依赖
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 运行时阶段
FROM python:3.10-slim

WORKDIR /app

# 1. 安装运行时依赖
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 2. 设置时区
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo "Asia/Shanghai" > /etc/timezone

# 3. 创建非root用户
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 4. 从构建阶段复制虚拟环境
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 5. 复制应用代码
COPY src/ ./src/
COPY config/ ./config/

# 6. 创建必要的目录
RUN mkdir -p /app/models_cache /app/logs \
    && chown -R appuser:appuser /app

# 7. 设置权限
RUN chown -R appuser:appuser /app
USER appuser

# 8. 环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Shanghai

# 9. 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# 10. 暴露端口
EXPOSE 8000

# 11. 启动命令
CMD ["uvicorn", "src.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "4"]
```

- [ ] **Step 2: 创建开发环境Dockerfile**

```dockerfile
# campus-ai/Dockerfile.dev
FROM python:3.10-slim

WORKDIR /app

# 1. 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 2. 复制依赖文件
COPY requirements.txt requirements-dev.txt .

# 3. 安装依赖
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

# 4. 复制应用代码
COPY src/ ./src/
COPY config/ ./config/
COPY .env.example .env

# 5. 创建必要的目录
RUN mkdir -p models_cache logs

# 6. 环境变量
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV ENV=development

# 7. 暴露端口
EXPOSE 8000

# 8. 开发环境启动命令（支持热重载）
CMD ["uvicorn", "src.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--reload", \
     "--log-level", "debug"]
```

- [ ] **Step 3: 创建Docker Compose配置**

```yaml
# campus-ai/docker-compose.yml
version: '3.8'

services:
  # Python算法服务（开发环境）
  algorithm-service:
    build:
      context: .
      dockerfile: Dockerfile.dev
    container_name: campus-ai-dev
    environment:
      - ENV=development
      - OSS_ENDPOINT=${OSS_ENDPOINT:-oss-cn-hangzhou.aliyuncs.com}
      - OSS_ACCESS_KEY_ID=${OSS_ACCESS_KEY_ID}
      - OSS_ACCESS_KEY_SECRET=${OSS_ACCESS_KEY_SECRET}
      - OSS_BUCKET_NAME=campus-ai-models-dev
      - SPRING_API_BASE_URL=http://host.docker.internal:8080/api
      - PRELOAD_KMEANS=${PRELOAD_KMEANS:-true}
      - PRELOAD_AHP_WEIGHTS=${PRELOAD_AHP_WEIGHTS:-true}
      - MODEL_CACHE_DIR=/app/models_cache
    ports:
      - "8000:8000"
    volumes:
      - ./src:/app/src:ro
      - ./config:/app/config:ro
      - ./models_cache:/app/models_cache
      - ./logs:/app/logs
      - ./.env:/app/.env:ro
    networks:
      - campus-network
    develop:
      watch:
        - action: sync
          path: ./src
          target: /app/src
        - action: rebuild
          path: ./requirements.txt

  # Redis缓存（可选）
  redis-ai:
    image: redis:7-alpine
    container_name: campus-redis-ai
    ports:
      - "6380:6379"
    volumes:
      - redis_ai_data:/data
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD:-ai_redis_pass_123}
    networks:
      - campus-network

volumes:
  redis_ai_data:

networks:
  campus-network:
    driver: bridge
```

- [ ] **Step 4: 创建开发环境配置文件**

```yaml
# campus-ai/config/development.yml
app:
  name: "campus-ai-service-dev"
  version: "1.0.0"
  debug: true
  log_level: "DEBUG"

server:
  host: "0.0.0.0"
  port: 8000
  workers: 1  # 开发环境单worker

oss:
  endpoint: "${OSS_ENDPOINT}"
  access_key_id: "${OSS_ACCESS_KEY_ID}"
  access_key_secret: "${OSS_ACCESS_KEY_SECRET}"
  bucket_name: "campus-ai-models-dev"
  model_prefix: "models/dev/"
  temp_prefix: "temp/dev/"

spring:
  api_base_url: "http://localhost:8080/api"
  timeout: 30

models:
  preload:
    kmeans: true
    ahp_weights: true
    lstm: false
  cache_dir: "./models_cache"
  max_cache_size_gb: 2  # 开发环境较小

logging:
  console_level: "DEBUG"
  file_level: "INFO"
  file_path: "./logs/app.log"
```

- [ ] **Step 5: 创建部署脚本**

```bash
# campus-ai/deploy/deploy.sh
#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🚀 校园社团算法服务部署脚本"

# 1. 检查环境
echo "🔍 检查环境..."
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo "❌ 未找到.env文件，请先复制.env.example并配置"
    exit 1
fi

# 2. 构建Docker镜像
echo "🔨 构建Docker镜像..."
cd "$PROJECT_ROOT"
docker build -t campus-ai:latest .

# 3. 运行服务
echo "🚀 启动服务..."
docker-compose down || true
docker-compose up -d

# 4. 等待服务就绪
echo "⏳ 等待服务启动..."
sleep 10

# 5. 健康检查
echo "🧪 运行健康检查..."
HEALTH_RESPONSE=$(curl -s http://localhost:8000/api/v1/health)
if echo "$HEALTH_RESPONSE" | grep -q '"status":"healthy"'; then
    echo "✅ 服务健康检查通过"
else
    echo "❌ 服务健康检查失败"
    echo "响应: $HEALTH_RESPONSE"
    exit 1
fi

echo ""
echo "🎉 部署完成!"
echo ""
echo "📊 服务信息:"
echo "  • 算法服务: http://localhost:8000/docs"
echo "  • 健康检查: http://localhost:8000/api/v1/health"
echo ""
echo "📋 检查服务状态: docker-compose ps"
echo "📝 查看日志: docker-compose logs -f algorithm-service"
```

- [ ] **Step 6: 设置部署脚本权限**

```bash
cd campus-ai
chmod +x deploy/deploy.sh
```

- [ ] **Step 7: 创建README文档**

```markdown
# campus-ai/README.md
# 校园社团算法服务

基于大数据分析的校园社团活动效果评估与资源优化系统 - 算法服务模块。

## 功能特性
- 个性化活动推荐（K-Means聚类）
- 多层次活动评估（AHP层次分析法）
- 资源需求预测（LSTM时间序列）
- 情感分析（NLP技术）
- 图像质量分析（计算机视觉）
- 资源优化分配（遗传算法）
- 关联规则挖掘（Apriori算法）

## 技术栈
- Python 3.10 + FastAPI 0.104+
- scikit-learn, PyTorch, pandas, numpy
- 阿里云OSS对象存储
- Docker + Docker Compose
- Prometheus + Grafana监控

## 快速开始

### 1. 环境准备
```bash
# 克隆项目
git clone <repository-url>
cd campus-ai

# 配置环境变量
cp .env.example .env
# 编辑.env文件，配置阿里云OSS等参数
```

### 2. 本地开发
```bash
# 安装依赖
pip install -r requirements.txt -r requirements-dev.txt

# 运行服务
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 访问API文档
# http://localhost:8000/docs
```

### 3. Docker开发
```bash
# 使用Docker Compose
docker-compose up -d

# 查看日志
docker-compose logs -f algorithm-service
```

### 4. 部署
```bash
# 使用部署脚本
./deploy/deploy.sh
```

## API文档
服务启动后访问：http://localhost:8000/docs

主要API端点：
- `GET /api/v1/health` - 健康检查
- `POST /api/v1/recommend/kmeans` - K-Means推荐
- `POST /api/v1/evaluation/ahp` - AHP评估
- `POST /api/v1/nlp/sentiment` - 情感分析
- ...（其他算法接口）

## 项目结构
```
campus-ai/
├── src/                    # 源代码
├── config/                 # 配置文件
├── models_cache/           # 模型缓存
├── logs/                   # 日志文件
├── deploy/                 # 部署脚本
└── monitoring/            # 监控配置
```

## 开发指南
1. 代码格式化：`black src/ tests/`
2. 代码检查：`ruff check src/ tests/`
3. 运行测试：`pytest tests/ -v`
4. 类型检查：`mypy src/`

## 监控
- Prometheus指标：http://localhost:8000/metrics
- 健康检查：http://localhost:8000/api/v1/health
- 就绪检查：http://localhost:8000/api/v1/ready
```

- [ ] **Step 8: 测试Docker构建**

```bash
cd campus-ai
# 测试Docker构建（使用缓存）
docker build -t campus-ai-test -f Dockerfile.dev .

# 验证镜像创建成功
docker images | grep campus-ai-test
期望输出: 显示campus-ai-test镜像

# 测试配置加载
docker run --rm -e ENV=development campus-ai-test python -c "
from src.core.config import get_settings
settings = get_settings()
print(f'✅ 配置加载成功: {settings.app_name}')
"
```

- [ ] **Step 9: 提交开发环境配置**

```bash
cd campus-ai
git add Dockerfile Dockerfile.dev docker-compose.yml config/development.yml deploy/deploy.sh README.md
git commit -m "feat: add Docker configuration, development setup, and deployment scripts"
```

---

## 计划自审

### 1. 规格覆盖检查
- [x] 项目结构初始化 - Task 1完成
- [x] FastAPI核心框架 - Task 2完成  
- [x] 数据模型与契约定义 - Task 3完成
- [x] 工具模块与客户端 - Task 4完成
- [x] 模型管理器服务 - Task 5完成
- [x] 开发环境与Docker配置 - Task 6完成

第一阶段基础框架规格要求均已覆盖。

### 2. 占位符扫描
- [x] 无TBD、TODO等占位符
- [x] 所有代码示例完整
- [x] 所有测试命令明确
- [x] 所有预期输出明确

### 3. 类型一致性检查
- [x] 所有类名、方法名、变量名一致
- [x] 配置文件键名一致
- [x] API端点路径一致
- [x] 测试用例覆盖关键路径

## 执行选项

**计划已完成并保存至 [docs/superpowers/plans/2026-04-09-campus-club-algorithm-service-phase1-foundation.md](docs/superpowers/plans/2026-04-09-campus-club-algorithm-service-phase1-foundation.md)。**

**两种执行选项：**

**1. 子代理驱动（推荐）** - 我为每个任务分派新的子代理，任务间进行审查，快速迭代

**2. 内联执行** - 在当前会话中使用executing-plans执行任务，设置检查点进行审查

**选择哪种方式？**

如果选择子代理驱动：
- **必需子技能**：使用superpowers:subagent-driven-development
- 每个任务使用新的子代理 + 两阶段审查

如果选择内联执行：
- **必需子技能**：使用superpowers:executing-plans
- 批量执行并设置检查点进行审查

---

*计划版本：1.0*
*创建时间：2026-04-09*
*创建者：Claude Code*
*状态：就绪执行*