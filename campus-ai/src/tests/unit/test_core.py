"""核心模块测试"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime

from src.core.config import get_settings, Settings
from src.core.exceptions import (
    AlgorithmServiceException,
    ModelNotFoundException,
    InvalidInputDataException,
    AlgorithmExecutionException
)
from src.main import app


def test_settings_loading():
    """测试配置加载"""
    settings = get_settings()

    assert isinstance(settings, Settings)
    assert settings.app_name == "campus-ai-service"
    assert settings.app_version == "1.0.0"
    assert settings.debug is False
    assert settings.log_level == "INFO"

    # 测试默认值
    assert settings.api_prefix == "/api/v1"
    assert settings.cors_origins == ["http://localhost:3000", "http://localhost:5173"]
    assert settings.oss_bucket_name == "campus-ai-models-dev"
    assert settings.spring_api_base_url == "http://localhost:8080/api"


def test_settings_env_override(monkeypatch):
    """测试环境变量覆盖配置"""
    monkeypatch.setenv("APP_NAME", "test-service")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    # 重新导入以应用环境变量
    import importlib
    import src.core.config
    importlib.reload(src.core.config)

    settings = src.core.config.get_settings()

    assert settings.app_name == "test-service"
    assert settings.debug is True
    assert settings.log_level == "DEBUG"

    # 恢复默认
    importlib.reload(src.core.config)


def test_exception_classes():
    """测试异常类"""
    # 测试基础异常
    exc = AlgorithmServiceException(
        status_code=400,
        detail="测试错误",
        error_code="TEST_ERROR",
        metadata={"field": "test"}
    )

    assert exc.status_code == 400
    assert exc.detail["error_code"] == "TEST_ERROR"
    assert exc.detail["message"] == "测试错误"
    assert exc.detail["metadata"]["field"] == "test"

    # 测试ModelNotFoundException
    model_exc = ModelNotFoundException("kmeans", "v1.0")
    assert model_exc.status_code == 404
    assert "kmeans" in model_exc.detail["message"]
    assert model_exc.detail["metadata"]["model_type"] == "kmeans"
    assert model_exc.detail["metadata"]["version"] == "v1.0"

    # 测试InvalidInputDataException
    input_exc = InvalidInputDataException("user_id", "不能为空", "null")
    assert input_exc.status_code == 400
    assert "user_id" in input_exc.detail["message"]
    assert input_exc.detail["metadata"]["field"] == "user_id"

    # 测试AlgorithmExecutionException
    algo_exc = AlgorithmExecutionException("kmeans", "聚类失败", 123.5)
    assert algo_exc.status_code == 500
    assert "kmeans" in algo_exc.detail["message"]
    assert algo_exc.detail["metadata"]["algorithm"] == "kmeans"


def test_health_endpoint():
    """测试健康检查端点"""
    client = TestClient(app)

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "healthy"
    assert data["service"] == "campus-ai-algorithm-service"
    assert "timestamp" in data
    assert "version" in data

    # 验证时间戳格式
    try:
        datetime.fromisoformat(data["timestamp"].replace('Z', '+00:00'))
    except ValueError:
        pytest.fail("时间戳格式无效")


def test_ready_endpoint():
    """测试就绪检查端点"""
    client = TestClient(app)

    response = client.get("/api/v1/ready")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] in ["ready", "not_ready"]
    assert "timestamp" in data
    assert "dependencies" in data
    assert isinstance(data["dependencies"], dict)

    # 验证依赖项结构
    deps = data["dependencies"]
    assert "config_loaded" in deps
    assert "model_cache_available" in deps
    assert "oss_connection" in deps


def test_docs_endpoints():
    """测试文档端点"""
    client = TestClient(app)

    # 测试OpenAPI文档
    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

    # 测试OpenAPI JSON
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    data = response.json()

    assert "openapi" in data
    assert "info" in data
    assert "paths" in data

    # 验证API信息
    assert data["info"]["title"] == "campus-ai-service"
    assert data["info"]["version"] == "1.0.0"


def test_cors_headers():
    """测试CORS头"""
    client = TestClient(app)

    # 测试预检请求
    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET"
        }
    )

    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_monitoring_endpoint():
    """测试监控端点"""
    client = TestClient(app)

    response = client.get("/metrics")

    # Prometheus端点应该返回成功
    assert response.status_code == 200
    assert "text/plain" in response.headers.get("content-type", "")


def test_app_lifespan():
    """测试应用生命周期（简化测试）"""
    # 测试应用可以正常创建
    assert app.title == "campus-ai-service"
    assert app.version == "1.0.0"
    assert app.description == "校园社团活动评估系统 - 算法服务"

    # 测试路由注册
    routes = [route.path for route in app.routes]
    assert "/api/v1/health" in routes
    assert "/docs" in routes
    assert "/redoc" in routes
    assert "/api/v1/openapi.json" in routes