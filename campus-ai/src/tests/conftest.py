"""测试配置文件"""

import pytest
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 测试环境设置
os.environ["ENV"] = "test"
os.environ["DEBUG"] = "true"
os.environ["LOG_LEVEL"] = "WARNING"  # 测试时减少日志输出


@pytest.fixture(scope="session")
def test_settings():
    """测试配置"""
    from src.core.config import get_settings
    return get_settings()


@pytest.fixture
def client():
    """测试客户端"""
    from fastapi.testclient import TestClient
    from src.main import app
    return TestClient(app)


@pytest.fixture(autouse=True)
def cleanup_env():
    """每个测试后清理环境变量"""
    # 保存原始环境变量
    original_env = os.environ.copy()

    yield

    # 恢复环境变量
    os.environ.clear()
    os.environ.update(original_env)