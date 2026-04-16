"""
预测分析 API
提供活动参与度预测、资源需求预测等功能
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from ...forecasting.memory_efficient_forecaster import MemoryEfficientForecaster
from ...tasks.forecasting_tasks import predict_participation_task

router = APIRouter(prefix="/forecasting", tags=["v3-forecasting"])

# 初始化预测器
forecaster = MemoryEfficientForecaster()


class ParticipationPredictionRequest(BaseModel):
    """参与度预测请求"""
    activity_type: str = Field(..., description="活动类型")
    venue_type: str = Field(..., description="场地类型")
    planned_date: str = Field(..., description="计划日期 (ISO格式)")
    historical_data: Optional[List[Dict]] = Field(default=None, description="历史数据")

    class Config:
        json_schema_extra = {
            "example": {
                "activity_type": "学术讲座",
                "venue_type": "大礼堂",
                "planned_date": "2024-04-20",
                "historical_data": [
                    {"date": "2024-01-15", "value": 150},
                    {"date": "2024-02-20", "value": 180},
                    {"date": "2024-03-15", "value": 200}
                ]
            }
        }


class ParticipationPredictionResponse(BaseModel):
    """参与度预测响应"""
    success: bool = True
    predicted_participants: int = Field(..., description="预测参与人数")
    confidence_lower: int = Field(..., description="置信区间下限")
    confidence_upper: int = Field(..., description="置信区间上限")
    confidence_score: float = Field(..., description="置信度评分 0-1")
    trend: str = Field(..., description="趋势: 上升/下降/平稳")
    recommendations: List[str] = Field(default=[], description="优化建议")


class ResourceDemandRequest(BaseModel):
    """资源需求预测请求"""
    resource_type: str = Field(..., description="资源类型: VENUE/EQUIPMENT")
    date_range: int = Field(default=30, description="预测天数", ge=1, le=90)

    class Config:
        json_schema_extra = {
            "example": {
                "resource_type": "VENUE",
                "date_range": 30
            }
        }


class ResourceDemandResponse(BaseModel):
    """资源需求预测响应"""
    success: bool = True
    resource_type: str
    predictions: List[Dict] = Field(..., description="每日预测数据")
    peak_dates: List[str] = Field(..., description="需求高峰日期")
    low_dates: List[str] = Field(..., description="需求低谷日期")
    average_demand: float = Field(..., description="平均需求")
    max_demand: int = Field(..., description="最大需求")


class PredictionTaskRequest(BaseModel):
    """异步预测任务请求"""
    task_type: str = Field(..., description="任务类型: participation/resource_demand")
    parameters: Dict = Field(..., description="任务参数")


class PredictionTaskResponse(BaseModel):
    """异步预测任务响应"""
    success: bool = True
    task_id: str = Field(..., description="任务ID")
    status: str = Field(..., description="任务状态: pending/running/completed/failed")
    estimated_duration: int = Field(..., description="预计执行时间(秒)")


@router.post("/participation", response_model=ParticipationPredictionResponse)
async def predict_participation(request: ParticipationPredictionRequest):
    """
    预测活动参与度

    基于历史数据和活动特征，预测未来活动的参与人数。

    - **预测依据**: 活动类型、场地类型、历史参与数据
    - **置信区间**: 提供预测结果的上下限范围
    - **趋势分析**: 分析参与人数变化趋势
    """
    try:
        import pandas as pd

        # 准备历史数据
        if request.historical_data:
            df = pd.DataFrame(request.historical_data)
        else:
            # 使用模拟数据
            df = pd.DataFrame({
                'date': pd.date_range(end=datetime.now(), periods=30, freq='D'),
                'value': [100 + i * 5 for i in range(30)]
            })

        # 获取或创建模型
        model = forecaster.get_or_create_model(
            request.activity_type,
            request.venue_type,
            df
        )

        # 预测
        future_date = datetime.fromisoformat(request.planned_date)
        future_dates = pd.date_range(start=future_date, periods=1, freq='D')
        prediction = model.predict(future_dates)

        predicted_value = int(prediction['yhat'].iloc[0])
        lower_bound = int(prediction['yhat_lower'].iloc[0])
        upper_bound = int(prediction['yhat_upper'].iloc[0])

        # 计算置信度
        confidence = 0.7 + (0.2 if len(df) > 10 else 0.1)

        # 趋势分析
        if len(df) > 1:
            recent_avg = df['value'].tail(7).mean()
            older_avg = df['value'].head(7).mean()
            if recent_avg > older_avg * 1.1:
                trend = "上升"
            elif recent_avg < older_avg * 0.9:
                trend = "下降"
            else:
                trend = "平稳"
        else:
            trend = "平稳"

        # 生成建议
        recommendations = []
        if predicted_value > 200:
            recommendations.append("预计参与人数较多，建议准备大场地")
        elif predicted_value < 50:
            recommendations.append("预计参与人数较少，建议加强宣传")

        if trend == "下降":
            recommendations.append("参与人数呈下降趋势，建议分析原因并改进")

        return ParticipationPredictionResponse(
            success=True,
            predicted_participants=predicted_value,
            confidence_lower=lower_bound,
            confidence_upper=upper_bound,
            confidence_score=round(confidence, 2),
            trend=trend,
            recommendations=recommendations
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"预测失败: {str(e)}")


@router.post("/resource-demand", response_model=ResourceDemandResponse)
async def predict_resource_demand(request: ResourceDemandRequest):
    """
    预测资源需求

    预测未来一段时间内各类资源的需求情况，帮助提前规划。

    - **预测范围**: 支持 1-90 天的需求预测
    - **高峰识别**: 自动识别需求高峰和低谷日期
    - **资源类型**: 支持场地、设备等资源类型
    """
    try:
        import pandas as pd
        import numpy as np

        # 生成模拟历史数据
        dates = pd.date_range(end=datetime.now(), periods=60, freq='D')
        base_demand = 50 if request.resource_type == "VENUE" else 30

        # 模拟数据：周末需求高
        values = []
        for i, date in enumerate(dates):
            is_weekend = date.weekday() >= 5
            base = base_demand * 1.5 if is_weekend else base_demand
            noise = np.random.normal(0, base * 0.1)
            values.append(max(0, int(base + noise)))

        df = pd.DataFrame({'date': dates, 'value': values})

        # 预测
        model = forecaster.get_or_create_model(
            request.resource_type,
            "default",
            df
        )

        future_dates = pd.date_range(
            start=datetime.now(),
            periods=request.date_range,
            freq='D'
        )
        predictions_df = model.predict(future_dates)

        # 处理预测结果
        predictions = []
        peak_dates = []
        low_dates = []

        for i, row in predictions_df.iterrows():
            date_str = row['ds'].strftime('%Y-%m-%d')
            value = int(row['yhat'])

            predictions.append({
                'date': date_str,
                'predicted_demand': value,
                'lower_bound': int(row['yhat_lower']),
                'upper_bound': int(row['yhat_upper'])
            })

        # 识别高峰和低谷
        all_values = [p['predicted_demand'] for p in predictions]
        avg_demand = sum(all_values) / len(all_values)
        threshold_high = avg_demand * 1.2
        threshold_low = avg_demand * 0.8

        for p in predictions:
            if p['predicted_demand'] > threshold_high:
                peak_dates.append(p['date'])
            elif p['predicted_demand'] < threshold_low:
                low_dates.append(p['date'])

        return ResourceDemandResponse(
            success=True,
            resource_type=request.resource_type,
            predictions=predictions,
            peak_dates=peak_dates[:5],  # 最多5个
            low_dates=low_dates[:5],
            average_demand=round(avg_demand, 1),
            max_demand=max(all_values)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"资源需求预测失败: {str(e)}")


@router.post("/async", response_model=PredictionTaskResponse)
async def create_prediction_task(
    request: PredictionTaskRequest,
    background_tasks: BackgroundTasks
):
    """
    创建异步预测任务

    对于耗时较长的预测任务，使用异步方式执行。

    - **适用场景**: 大规模数据预测、复杂模型训练
    - **任务状态**: 通过 /tasks/{task_id} 查询进度
    - **执行时间**: 5-10分钟不等
    """
    try:
        # 生成任务ID
        import uuid
        task_id = str(uuid.uuid4())

        # 提交异步任务
        if request.task_type == "participation":
            background_tasks.add_task(
                predict_participation_task,
                task_id,
                request.parameters
            )
            estimated_duration = 60
        else:
            estimated_duration = 120

        return PredictionTaskResponse(
            success=True,
            task_id=task_id,
            status="pending",
            estimated_duration=estimated_duration
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建预测任务失败: {str(e)}")


@router.get("/cache-stats")
async def get_cache_stats():
    """获取预测模型缓存统计"""
    return forecaster.get_cache_stats()


@router.get("/health")
async def health_check():
    """预测服务健康检查"""
    return {"status": "healthy", "service": "forecasting-prediction"}
