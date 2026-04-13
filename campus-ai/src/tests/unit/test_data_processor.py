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