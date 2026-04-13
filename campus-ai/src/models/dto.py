from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import numpy as np

@dataclass
class ProcessedActivity:
    """清洗后的活动数据"""
    activity_id: str
    activity_type: str
    features: np.ndarray  # 数值化特征向量
    metadata: Dict[str, Any]
    is_valid: bool = True
    validation_errors: List[str] = None

    def __post_init__(self):
        if self.validation_errors is None:
            self.validation_errors = []

@dataclass
class ModelPrediction:
    """模型预测结果"""
    model_type: str
    prediction: Any
    confidence: float
    metadata: Dict[str, Any]
    execution_time_ms: float

@dataclass
class BatchProcessingResult:
    """批处理结果"""
    successful_count: int
    failed_count: int
    errors: List[Dict[str, Any]]
    total_processing_time_ms: float