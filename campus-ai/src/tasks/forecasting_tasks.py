# campus-ai/src/tasks/forecasting_tasks.py

from celery import shared_task
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from forecasting.memory_efficient_forecaster import MemoryEfficientForecaster


@shared_task(bind=True, max_retries=2, soft_time_limit=300)
def train_forecasting_model(
    self,
    activity_type: str,
    venue_type: str,
    historical_data: List[Dict],
    model_dir: str = "./models/forecasting"
) -> Dict:
    """
    异步训练预测模型

    时间预估: 10-30秒
    """
    try:
        # 转换数据
        df = pd.DataFrame(historical_data)

        # 创建预测器
        forecaster = MemoryEfficientForecaster(model_dir=model_dir)

        # 训练模型
        model = forecaster.get_or_create_model(
            activity_type=activity_type,
            venue_type=venue_type,
            historical_data=df
        )

        # 获取缓存统计
        stats = forecaster.get_cache_stats()

        return {
            "status": "success",
            "activity_type": activity_type,
            "venue_type": venue_type,
            "model_id": forecaster._get_model_id(activity_type, venue_type),
            "cache_stats": stats
        }

    except Exception as exc:
        self.retry(exc=exc, countdown=30)


@shared_task(bind=True, max_retries=3)
def predict_activity_attendance(
    self,
    activity_type: str,
    venue_type: str,
    periods: int = 30,
    model_dir: str = "./models/forecasting"
) -> Dict:
    """
    异步预测活动参与度

    时间预估: < 100ms (缓存命中) / 5-10s (需训练)
    """
    try:
        # 创建预测器
        forecaster = MemoryEfficientForecaster(model_dir=model_dir)

        # 创建模拟历史数据（实际应从数据库获取）
        historical_data = _get_historical_data(activity_type, venue_type)

        # 预测
        forecast = forecaster.predict(
            activity_type=activity_type,
            venue_type=venue_type,
            periods=periods,
            historical_data=historical_data
        )

        # 转换结果为可序列化格式
        forecast_list = forecast.to_dict('records')
        for item in forecast_list:
            item['ds'] = item['ds'].isoformat() if isinstance(item['ds'], datetime) else item['ds']

        return {
            "status": "success",
            "activity_type": activity_type,
            "venue_type": venue_type,
            "forecast": forecast_list,
            "cache_stats": forecaster.get_cache_stats()
        }

    except Exception as exc:
        self.retry(exc=exc, countdown=10)


def _get_historical_data(activity_type: str, venue_type: str) -> pd.DataFrame:
    """获取历史数据（模拟实现）"""
    # 实际实现应从数据库查询
    np.random.seed(42)
    dates = pd.date_range(end=datetime.now(), periods=365, freq='D')
    values = np.random.poisson(lam=50, size=365) + np.random.normal(0, 10, 365)

    return pd.DataFrame({
        'date': dates,
        'value': values
    })
