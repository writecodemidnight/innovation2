from pydantic import BaseModel, Field, field_validator
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
        min_length=3
    )
    top_n: int = Field(5, ge=1, le=20, description="推荐数量")
    include_metadata: bool = Field(False, description="是否包含活动元数据")

    @field_validator("history_activities")
    @classmethod
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
        min_length=1,
        max_length=100
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