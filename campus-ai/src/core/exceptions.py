from fastapi import HTTPException, status
from typing import Any, Dict, Optional

class AlgorithmServiceException(HTTPException):
    """算法服务基础异常"""

    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status_code,
            detail={
                "error_code": error_code,
                "message": detail,
                "metadata": metadata or {}
            }
        )

# ============ 特定业务异常 ============
class ModelNotFoundException(AlgorithmServiceException):
    """模型未找到异常"""
    def __init__(self, model_type: str, version: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"模型 '{model_type}' 未找到" + (f" (版本: {version})" if version else ""),
            error_code="MODEL_NOT_FOUND",
            metadata={"model_type": model_type, "version": version}
        )

class InvalidInputDataException(AlgorithmServiceException):
    """输入数据异常"""
    def __init__(self, field: str, reason: str, received_value: Any = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"字段 '{field}' 数据无效: {reason}",
            error_code="INVALID_INPUT_DATA",
            metadata={
                "field": field,
                "reason": reason,
                "received_value": str(received_value)[:100]
            }
        )

class AlgorithmExecutionException(AlgorithmServiceException):
    """算法执行异常"""
    def __init__(self, algorithm: str, reason: str, execution_time: Optional[float] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"算法 '{algorithm}' 执行失败: {reason}",
            error_code="ALGORITHM_EXECUTION_ERROR",
            metadata={
                "algorithm": algorithm,
                "reason": reason,
                "execution_time_ms": execution_time
            }
        )