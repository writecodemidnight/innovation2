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
    # 使用MagicMock模拟同步的json()方法
    mock_response.json = MagicMock(return_value={
        "user_id": "user_001",
        "activities": [
            {"activity_id": "act_001", "title": "Test Activity"}
        ]
    })
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
    # 使用MagicMock模拟同步的json()方法（虽然这里不需要返回值）
    mock_response.json = MagicMock(return_value={})
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