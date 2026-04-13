import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from loguru import logger
from datetime import datetime

from ..models.schemas import HistoryActivity
from ..models.dto import ProcessedActivity

class DataProcessor:
    """数据清洗与预处理服务"""

    def __init__(self):
        self.imputation_strategies = {
            'mean': self._impute_with_mean,
            'median': self._impute_with_median,
            'mode': self._impute_with_mode,
            'constant': self._impute_with_constant
        }

    async def clean_activity_data(
        self,
        activities: List[HistoryActivity]
    ) -> Tuple[List[ProcessedActivity], List[str]]:
        """清洗活动数据，处理空值和异常"""
        processed = []
        errors = []

        for i, activity in enumerate(activities):
            try:
                # 1. 基础验证
                if not activity.activity_id:
                    errors.append(f"活动{i}: 缺少activity_id")
                    continue

                if not activity.activity_type:
                    errors.append(f"活动{i}: 缺少activity_type")
                    continue

                # 2. 数值字段处理
                participation_score = self._handle_missing_value(
                    activity.participation_score,
                    strategy='median',
                    default_value=50.0
                )

                feedback_score = self._handle_missing_value(
                    activity.feedback_score,
                    strategy='median',
                    default_value=3.0
                )

                # 3. 特征工程
                features = self._extract_activity_features(
                    activity_type=activity.activity_type.value,
                    participation_score=participation_score,
                    feedback_score=feedback_score,
                    timestamp=activity.timestamp
                )

                processed.append(ProcessedActivity(
                    activity_id=activity.activity_id,
                    activity_type=activity.activity_type.value,
                    features=features,
                    metadata={
                        'original_participation_score': activity.participation_score,
                        'original_feedback_score': activity.feedback_score,
                        'processed_timestamp': activity.timestamp.isoformat()
                    }
                ))

            except Exception as e:
                errors.append(f"活动{i}处理失败: {str(e)}")
                logger.error(f"活动数据清洗失败: {e}")

        return processed, errors

    def _handle_missing_value(self, value, strategy='median', default_value=None):
        """处理缺失值"""
        if value is None:
            if strategy in self.imputation_strategies:
                return self.imputation_strategies[strategy](default_value)
            return default_value
        return value

    def _extract_activity_features(
        self,
        activity_type: str,
        participation_score: float,
        feedback_score: float,
        timestamp: datetime
    ) -> np.ndarray:
        """提取活动特征向量"""
        features = []

        # 1. 活动类型one-hot编码
        activity_types = ['lecture', 'workshop', 'competition', 'social', 'sports', 'volunteer']
        type_vector = [1 if activity_type == t else 0 for t in activity_types]
        features.extend(type_vector)

        # 2. 数值特征
        features.append(participation_score / 100.0)  # 归一化到0-1
        features.append((feedback_score - 1) / 4.0)   # 归一化到0-1

        # 3. 时间特征（周期性编码）
        hour_sin = np.sin(2 * np.pi * timestamp.hour / 24)
        hour_cos = np.cos(2 * np.pi * timestamp.hour / 24)
        day_sin = np.sin(2 * np.pi * timestamp.weekday() / 7)
        day_cos = np.cos(2 * np.pi * timestamp.weekday() / 7)

        features.extend([hour_sin, hour_cos, day_sin, day_cos])

        return np.array(features)

    # 插补策略方法
    def _impute_with_mean(self, default_value=None):
        return 0.5  # 简化实现

    def _impute_with_median(self, default_value=None):
        return default_value if default_value is not None else 0.5

    def _impute_with_mode(self, default_value=None):
        return default_value if default_value is not None else 0.5

    def _impute_with_constant(self, default_value=None):
        return default_value if default_value is not None else 0.0