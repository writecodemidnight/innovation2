# campus-ai/tests/integration/test_api_v3.py
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# Skip all tests if FastAPI components are not available
pytestmark = [
    pytest.mark.skipif(
        not pytest.importorskip("fastapi", reason="FastAPI not installed"),
        reason="FastAPI not installed"
    ),
]


def test_v3_router_imports():
    """测试V3路由可以导入"""
    try:
        from api.v3 import v3_router
        assert v3_router is not None
    except ImportError as e:
        if "celery" in str(e).lower():
            pytest.skip("Celery not installed")
        raise


def test_clustering_router_imports():
    """测试聚类路由可以导入"""
    try:
        from api.v3.clustering import router as clustering_router
        assert clustering_router is not None
    except ImportError as e:
        if "celery" in str(e).lower():
            pytest.skip("Celery not installed")
        raise


def test_scheduling_router_imports():
    """测试调度路由可以导入"""
    try:
        from api.v3.scheduling import router as scheduling_router
        assert scheduling_router is not None
    except ImportError as e:
        if "celery" in str(e).lower():
            pytest.skip("Celery not installed")
        raise


def test_tasks_router_imports():
    """测试任务路由可以导入"""
    try:
        from api.v3.tasks import router as tasks_router
        assert tasks_router is not None
    except ImportError as e:
        if "celery" in str(e).lower():
            pytest.skip("Celery not installed")
        raise
