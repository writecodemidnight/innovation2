"""
NLP 自然语言处理 API
提供文本情感分析、关键词提取等功能
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Optional

from ...core.nlp_analyzer import NLPSentimentAnalyzer, SentimentResult

router = APIRouter(prefix="/nlp", tags=["v3-nlp"])

# 初始化分析器
analyzer = NLPSentimentAnalyzer()


class SentimentRequest(BaseModel):
    """情感分析请求"""
    text: str = Field(..., description="待分析的文本", min_length=1, max_length=5000)

    class Config:
        json_schema_extra = {
            "example": {
                "text": "活动组织得很好，学到了很多知识，期待下次参加！"
            }
        }


class SentimentResponse(BaseModel):
    """情感分析响应"""
    success: bool = True
    text: str = Field(..., description="原始文本")
    sentiment_score: float = Field(..., description="情感得分 0-1，越接近1越正面", ge=0, le=1)
    sentiment_level: str = Field(..., description="情感等级: 非常正面/正面/中性/负面/非常负面")
    confidence: float = Field(..., description="置信度", ge=0, le=1)
    keywords: List[str] = Field(default=[], description="提取的关键词")
    aspect_sentiments: Dict[str, float] = Field(default={}, description="各方面情感分析")


class BatchSentimentRequest(BaseModel):
    """批量情感分析请求"""
    texts: List[str] = Field(..., description="待分析的文本列表", max_length=100)

    class Config:
        json_schema_extra = {
            "example": {
                "texts": [
                    "活动组织得很好！",
                    "内容有点无聊，希望可以改进"
                ]
            }
        }


class BatchSentimentResponse(BaseModel):
    """批量情感分析响应"""
    success: bool = True
    results: List[SentimentResponse]
    average_score: float = Field(..., description="平均情感得分")
    positive_count: int = Field(..., description="正面评价数量")
    negative_count: int = Field(..., description="负面评价数量")
    neutral_count: int = Field(..., description="中性评价数量")


class ActivityFeedbackRequest(BaseModel):
    """活动反馈分析请求"""
    activity_id: str = Field(..., description="活动ID")
    feedbacks: List[Dict[str, str]] = Field(..., description="反馈列表")

    class Config:
        json_schema_extra = {
            "example": {
                "activity_id": "12345",
                "feedbacks": [
                    {"student_id": "S001", "text": "活动组织得很好！"},
                    {"student_id": "S002", "text": "学到了很多知识"}
                ]
            }
        }


class ActivityFeedbackResponse(BaseModel):
    """活动反馈分析响应"""
    success: bool = True
    activity_id: str
    total_feedback: int = Field(..., description="反馈总数")
    average_sentiment: float = Field(..., description="平均情感得分")
    sentiment_distribution: Dict[str, int] = Field(..., description="情感分布统计")
    key_aspects: Dict[str, float] = Field(..., description="关键方面评分")
    suggestions: List[str] = Field(default=[], description="改进建议")


@router.post("/sentiment", response_model=SentimentResponse)
async def analyze_sentiment(request: SentimentRequest):
    """
    单条文本情感分析

    分析学生反馈的情感倾向，返回情感得分、等级和关键词。

    - **情感得分**: 0-1之间，越接近1表示越正面
    - **情感等级**: 非常正面/正面/中性/负面/非常负面
    - **置信度**: 分析结果的可信度
    """
    try:
        result = analyzer.analyze(request.text)
        return SentimentResponse(
            success=True,
            text=result.text,
            sentiment_score=result.sentiment_score,
            sentiment_level=result.sentiment_level,
            confidence=result.confidence,
            keywords=result.keywords,
            aspect_sentiments=result.aspect_sentiments
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"情感分析失败: {str(e)}")


@router.post("/sentiment/batch", response_model=BatchSentimentResponse)
async def analyze_sentiment_batch(request: BatchSentimentRequest):
    """
    批量情感分析

    同时分析多条文本，适用于活动反馈批量处理场景。
    """
    try:
        results = analyzer.analyze_batch(request.texts)

        # 转换为响应格式
        response_results = [
            SentimentResponse(
                success=True,
                text=r.text,
                sentiment_score=r.sentiment_score,
                sentiment_level=r.sentiment_level,
                confidence=r.confidence,
                keywords=r.keywords,
                aspect_sentiments=r.aspect_sentiments
            )
            for r in results
        ]

        # 统计信息
        scores = [r.sentiment_score for r in results]
        avg_score = sum(scores) / len(scores) if scores else 0.5

        positive_count = sum(1 for r in results if r.sentiment_score > 0.6)
        negative_count = sum(1 for r in results if r.sentiment_score < 0.4)
        neutral_count = len(results) - positive_count - negative_count

        return BatchSentimentResponse(
            success=True,
            results=response_results,
            average_score=round(avg_score, 3),
            positive_count=positive_count,
            negative_count=negative_count,
            neutral_count=neutral_count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量分析失败: {str(e)}")


@router.post("/activity-feedback", response_model=ActivityFeedbackResponse)
async def analyze_activity_feedback(request: ActivityFeedbackRequest):
    """
    活动反馈综合分析

    分析整个活动的所有学生反馈，生成综合分析报告和改进建议。
    """
    try:
        result = analyzer.analyze_activity_feedback(
            request.activity_id,
            request.feedbacks
        )

        # 生成改进建议
        suggestions = analyzer.get_improvement_suggestions(result)

        return ActivityFeedbackResponse(
            success=True,
            activity_id=result["activity_id"],
            total_feedback=result["total_feedback"],
            average_sentiment=result["average_sentiment"],
            sentiment_distribution=result["sentiment_distribution"],
            key_aspects=result["key_aspects"],
            suggestions=suggestions
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"活动反馈分析失败: {str(e)}")


@router.get("/health")
async def health_check():
    """NLP服务健康检查"""
    return {"status": "healthy", "service": "nlp-sentiment-analysis"}
