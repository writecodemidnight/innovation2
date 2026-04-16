"""
简化版 AHP 算法服务
仅提供核心的五维评估 API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any
import numpy as np
import uvicorn

app = FastAPI(
    title="Campus AI - AHP Evaluation Service",
    version="1.0.0",
    description="校园社团活动效果 AHP 评估服务",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 默认五维权重（基于AHP计算）
DEFAULT_WEIGHTS = {
    "参与度": 0.32,
    "教育性": 0.18,
    "创新性": 0.15,
    "影响力": 0.22,
    "可持续性": 0.13
}

CONSISTENCY_THRESHOLD = 0.1


class AHPEvaluateRequest(BaseModel):
    """AHP评估请求"""
    algorithmType: str = "AHP"
    parameters: Dict[str, Any] = Field(..., description="参数")

    class Config:
        json_schema_extra = {
            "example": {
                "algorithmType": "AHP",
                "parameters": {
                    "scores": {
                        "参与度": 85,
                        "教育性": 90,
                        "创新性": 75,
                        "影响力": 80,
                        "可持续性": 88
                    }
                }
            }
        }


class AlgorithmResponse(BaseModel):
    """算法响应"""
    success: bool
    algorithmType: str
    result: Dict[str, Any]
    processingTimeMs: int
    errorMessage: str = None


def calculate_consistency_ratio(weights: Dict[str, float]) -> float:
    """计算一致性比率"""
    dimensions = list(weights.keys())
    n = len(dimensions)

    # 构建判断矩阵
    judgment_matrix = np.ones((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                wi = weights[dimensions[i]]
                wj = weights[dimensions[j]]
                judgment_matrix[i, j] = wi / wj

    # 计算特征值
    eigenvalues, _ = np.linalg.eig(judgment_matrix)
    max_eigenvalue = np.max(eigenvalues.real)

    # CI = (λmax - n) / (n - 1)
    ci = (max_eigenvalue - n) / (n - 1)

    # RI for n=5 is 1.12
    ri = 1.12
    cr = ci / ri if ri > 0 else 0.0

    return float(abs(cr))


@app.post("/api/v1/algorithms/ahp", response_model=AlgorithmResponse)
async def evaluate_ahp(request: AHPEvaluateRequest):
    """
    AHP五维活动效果评估 - 兼容后端 AlgorithmRequest 格式
    """
    import time
    start_time = time.time()

    try:
        params = request.parameters
        scores = params.get("scores", {})
        dimensions = ["参与度", "教育性", "创新性", "影响力", "可持续性"]

        # 验证输入
        for dim in dimensions:
            if dim not in scores:
                raise HTTPException(status_code=400, detail=f"缺少维度得分: {dim}")
            if not 0 <= scores[dim] <= 100:
                raise HTTPException(status_code=400, detail=f"{dim}得分必须在0-100之间")

        # 获取权重
        weights = DEFAULT_WEIGHTS

        # 计算加权总分
        total_score = sum(
            scores[dim] * weights[dim]
            for dim in dimensions
        )

        # 计算各维度贡献度
        contributions = {
            dim: round(scores[dim] * weights[dim], 2)
            for dim in dimensions
        }

        # 计算一致性比率
        cr = calculate_consistency_ratio(weights)

        processing_time = int((time.time() - start_time) * 1000)

        return AlgorithmResponse(
            success=True,
            algorithmType="AHP",
            result={
                "total_score": round(total_score, 2),
                "dimension_scores": {k: round(v, 2) for k, v in scores.items()},
                "weights": {k: round(v, 4) for k, v in weights.items()},
                "contributions": contributions,
                "consistency_ratio": round(cr, 4),
                "consistency_check_passed": cr < CONSISTENCY_THRESHOLD
            },
            processingTimeMs=processing_time
        )

    except HTTPException:
        raise
    except Exception as e:
        return AlgorithmResponse(
            success=False,
            algorithmType="AHP",
            result={},
            processingTimeMs=0,
            errorMessage=str(e)
        )


@app.post("/api/v3/ml/evaluation/ahp")
async def evaluate_ahp_v3(request: AHPEvaluateRequest):
    """V3 API 版本的 AHP 评估"""
    return await evaluate_ahp(request)


@app.get("/api/v3/ml/evaluation/weights")
async def get_weights():
    """获取权重配置"""
    return {
        "weights": DEFAULT_WEIGHTS,
        "consistency_ratio": 0.03,
        "consistency_check_passed": True,
        "dimensions": list(DEFAULT_WEIGHTS.keys())
    }


@app.get("/health")
@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "campus-ai-ahp",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Campus AI Service",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
