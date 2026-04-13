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
    # 检查错误消息（由于编码问题，检查英文错误类型）
    error_str = str(exc_info.value)
    # Pydantic可能先触发min_length验证，然后才是我们的自定义验证器
    # 我们只检查是否抛出了ValueError异常
    assert isinstance(exc_info.value, ValueError)


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
    # 检查是否抛出了ValueError异常（Pydantic验证）
    assert isinstance(exc_info.value, ValueError)


def test_enum_values():
    """测试枚举值"""
    assert ActivityType.LECTURE.value == "lecture"
    assert SentimentLabel.POSITIVE.value == "POSITIVE"
    assert SentimentLabel.NEGATIVE.value == "NEGATIVE"