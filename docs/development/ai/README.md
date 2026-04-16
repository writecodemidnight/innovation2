# Python 算法服务开发指南

本文档介绍 Python 算法服务的开发规范和算法实现。

---

## 目录

1. [项目结构](#项目结构)
2. [开发规范](#开发规范)
3. [核心算法实现](#核心算法实现)
4. [模型管理](#模型管理)
5. [性能优化](#性能优化)

---

## 项目结构

```
campus-ai/
├── src/
│   ├── api/                     # API 路由层
│   │   ├── health.py           # 健康检查
│   │   └── v3/                 # v3 版本接口
│   │       ├── __init__.py
│   │       ├── clustering.py   # K-Means 聚类
│   │       ├── evaluation.py   # AHP 评估
│   │       ├── scheduling.py   # GA/LSTM 调度
│   │       └── tasks.py        # 异步任务
│   │
│   ├── algorithms/              # 算法实现层
│   │   ├── __init__.py
│   │   ├── kmeans.py           # K-Means 实现
│   │   ├── ahp.py              # AHP 层次分析
│   │   ├── lstm.py             # LSTM 预测
│   │   ├── genetic.py          # 遗传算法
│   │   └── nlp.py              # NLP 情感分析
│   │
│   ├── core/                    # 核心配置
│   │   ├── __init__.py
│   │   ├── config.py           # 配置管理
│   │   ├── cache.py            # 缓存管理
│   │   └── model_manager.py    # 模型管理器
│   │
│   ├── models/                  # Pydantic 模型
│   │   ├── __init__.py
│   │   ├── requests.py         # 请求模型
│   │   └── responses.py        # 响应模型
│   │
│   └── main.py                  # 应用入口
│
├── tests/                       # 测试目录
├── models_cache/               # 模型缓存
│   ├── kmeans/
│   ├── lstm/
│   └── ahp/
├── config/                     # 配置文件
├── requirements.txt
└── Dockerfile
```

---

## 开发规范

### 代码风格

- 使用 **Black** 格式化代码
- 使用 **Ruff** 进行代码检查
- 使用 **MyPy** 进行类型检查
- 所有函数必须添加类型注解
- 使用 Google Style Docstrings

### 接口规范

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any

router = APIRouter(prefix="/evaluation", tags=["v3-evaluation"])


class EvaluateRequest(BaseModel):
    """评估请求模型"""
    scores: Dict[str, float] = Field(..., description="各维度得分")
    
    class Config:
        json_schema_extra = {
            "example": {
                "scores": {"参与度": 85, "教育性": 90}
            }
        }


class EvaluateResponse(BaseModel):
    """评估响应模型"""
    success: bool = True
    total_score: float = Field(..., description="总分")
    algorithm_version: str = "v1.0"


@router.post("/ahp", response_model=EvaluateResponse)
async def evaluate_ahp(request: EvaluateRequest) -> EvaluateResponse:
    """
    AHP五维评估
    
    Args:
        request: 包含各维度得分的请求
        
    Returns:
        包含总分和权重的评估结果
        
    Raises:
        HTTPException: 当输入参数无效时
    """
    try:
        # 验证输入
        if not request.scores:
            raise HTTPException(status_code=400, detail="得分不能为空")
            
        # 执行算法
        result = ahp_algorithm.calculate(request.scores)
        
        return EvaluateResponse(
            success=True,
            total_score=result.total,
            algorithm_version="AHP-v1.0"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"计算失败: {str(e)}")
```

---

## 核心算法实现

### 1. AHP 层次分析法

**文件**: `algorithms/ahp.py`

```python
import numpy as np
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class AHPResult:
    """AHP计算结果"""
    total_score: float
    dimension_scores: Dict[str, float]
    weights: Dict[str, float]
    contributions: Dict[str, float]
    consistency_ratio: float
    consistency_check_passed: bool


class AHPCalculator:
    """AHP层次分析法计算器"""
    
    # 默认五维权重
    DEFAULT_WEIGHTS = {
        "参与度": 0.32,
        "教育性": 0.18,
        "创新性": 0.15,
        "影响力": 0.22,
        "可持续性": 0.13
    }
    
    # 一致性阈值
    CR_THRESHOLD = 0.1
    
    # 随机一致性指标
    RI_TABLE = {1: 0, 2: 0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24}
    
    def __init__(self, weights: Dict[str, float] = None):
        self.weights = weights or self.DEFAULT_WEIGHTS
        self.dimensions = list(self.weights.keys())
    
    def calculate(self, scores: Dict[str, float]) -> AHPResult:
        """
        计算AHP评估结果
        
        Args:
            scores: 各维度得分，范围0-100
            
        Returns:
            AHPResult: 包含总分、权重、一致性检验结果
        """
        # 验证输入
        self._validate_scores(scores)
        
        # 计算加权总分
        total_score = sum(
            scores[dim] * self.weights[dim]
            for dim in self.dimensions
        )
        
        # 计算各维度贡献度
        contributions = {
            dim: round(scores[dim] * self.weights[dim], 2)
            for dim in self.dimensions
        }
        
        # 计算一致性比率
        judgment_matrix = self._build_judgment_matrix()
        cr = self._calculate_consistency_ratio(judgment_matrix)
        
        return AHPResult(
            total_score=round(total_score, 2),
            dimension_scores={k: round(v, 2) for k, v in scores.items()},
            weights={k: round(v, 4) for k, v in self.weights.items()},
            contributions=contributions,
            consistency_ratio=round(cr, 4),
            consistency_check_passed=cr < self.CR_THRESHOLD
        )
    
    def _validate_scores(self, scores: Dict[str, float]):
        """验证输入分数"""
        for dim in self.dimensions:
            if dim not in scores:
                raise ValueError(f"缺少维度得分: {dim}")
            if not 0 <= scores[dim] <= 100:
                raise ValueError(f"{dim}得分必须在0-100之间")
    
    def _build_judgment_matrix(self) -> np.ndarray:
        """构建判断矩阵"""
        n = len(self.dimensions)
        matrix = np.ones((n, n))
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    wi = self.weights[self.dimensions[i]]
                    wj = self.weights[self.dimensions[j]]
                    matrix[i, j] = wi / wj
        
        return matrix
    
    def _calculate_consistency_ratio(self, matrix: np.ndarray) -> float:
        """计算一致性比率"""
        n = matrix.shape[0]
        eigenvalues, _ = np.linalg.eig(matrix)
        max_eigenvalue = np.max(eigenvalues.real)
        
        # 一致性指标 CI = (λmax - n) / (n - 1)
        ci = (max_eigenvalue - n) / (n - 1)
        
        # 随机一致性指标RI
        ri = self.RI_TABLE.get(n, 1.12)
        
        # 一致性比率 CR = CI / RI
        return abs(ci / ri) if ri > 0 else 0.0
```

### 2. K-Means 聚类

**文件**: `algorithms/kmeans.py`

```python
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Any
import pickle
import os


class ClubClustering:
    """社团聚类分析器"""
    
    def __init__(self, n_clusters: int = 5, cache_dir: str = "models_cache/kmeans"):
        self.n_clusters = n_clusters
        self.cache_dir = cache_dir
        self.model: KMeans = None
        self.scaler: StandardScaler = None
        
        os.makedirs(cache_dir, exist_ok=True)
    
    def fit(self, features: np.ndarray) -> Dict[str, Any]:
        """
        训练聚类模型
        
        Args:
            features: 特征矩阵，shape=(n_samples, n_features)
            
        Returns:
            聚类结果统计
        """
        # 标准化
        self.scaler = StandardScaler()
        features_scaled = self.scaler.fit_transform(features)
        
        # 训练模型
        self.model = KMeans(
            n_clusters=self.n_clusters,
            random_state=42,
            n_init=10
        )
        labels = self.model.fit_predict(features_scaled)
        
        # 保存模型
        self._save_model()
        
        # 返回统计信息
        return {
            "n_clusters": self.n_clusters,
            "labels": labels.tolist(),
            "cluster_centers": self.model.cluster_centers_.tolist(),
            "inertia": float(self.model.inertia_)
        }
    
    def predict(self, features: np.ndarray) -> np.ndarray:
        """预测新数据"""
        if self.model is None:
            self._load_model()
        
        features_scaled = self.scaler.transform(features)
        return self.model.predict(features_scaled)
    
    def _save_model(self):
        """保存模型到缓存"""
        model_path = os.path.join(self.cache_dir, "kmeans_model.pkl")
        with open(model_path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'scaler': self.scaler
            }, f)
    
    def _load_model(self):
        """从缓存加载模型"""
        model_path = os.path.join(self.cache_dir, "kmeans_model.pkl")
        with open(model_path, 'rb') as f:
            data = pickle.load(f)
            self.model = data['model']
            self.scaler = data['scaler']
```

### 3. NLP 情感分析

**文件**: `algorithms/nlp.py`

```python
from transformers import pipeline
from typing import List, Dict
import jieba
import jieba.analyse


class NLPSentimentAnalyzer:
    """NLP情感分析器"""
    
    def __init__(self):
        # 使用中文情感分析模型
        self.sentiment_classifier = pipeline(
            "sentiment-analysis",
            model="uer/roberta-base-finetuned-jd-binary-chinese"
        )
        
        # 加载停用词
        jieba.analyse.set_stop_words("config/stopwords.txt")
    
    def analyze(self, text: str) -> Dict:
        """
        分析文本情感
        
        Args:
            text: 待分析的文本
            
        Returns:
            包含情感得分、情感级别、关键词的结果
        """
        # 1. 情感分类
        result = self.sentiment_classifier(text)[0]
        sentiment_label = result['label']
        sentiment_score = result['score']
        
        # 转换为 -1 到 1 的得分
        if sentiment_label == 'positive':
            normalized_score = sentiment_score
            level = 'POSITIVE'
        else:
            normalized_score = -sentiment_score
            level = 'NEGATIVE'
        
        # 2. 关键词提取
        keywords = jieba.analyse.extract_tags(text, topK=5, withWeight=True)
        
        # 3. 各方面情感分析 (简化版)
        aspect_sentiments = self._analyze_aspects(text)
        
        return {
            'sentiment_score': round(normalized_score, 4),
            'sentiment_level': level,
            'keywords': [kw[0] for kw in keywords],
            'aspect_sentiments': aspect_sentiments
        }
    
    def _analyze_aspects(self, text: str) -> Dict[str, float]:
        """分析各方面的情感"""
        # 预定义方面词
        aspects = {
            '活动组织': ['组织', '安排', '流程', '秩序'],
            '活动内容': ['内容', '主题', '知识', '收获'],
            '互动体验': ['互动', '参与', '体验', '氛围'],
            '时间地点': ['时间', '地点', '场地', '方便']
        }
        
        aspect_scores = {}
        for aspect, keywords in aspects.items():
            # 检查文本中是否包含方面词
            if any(kw in text for kw in keywords):
                # 提取相关句子进行分析
                # 这里简化处理，实际应提取完整句子
                aspect_scores[aspect] = 0.5  # 中性偏正面
        
        return aspect_scores
```

### 4. LSTM 预测模型

**文件**: `algorithms/lstm.py`

```python
import torch
import torch.nn as nn
import numpy as np
from typing import List, Tuple


class LSTMPredictor(nn.Module):
    """LSTM预测模型"""
    
    def __init__(self, input_size: int = 5, hidden_size: int = 64, num_layers: int = 2):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.2
        )
        
        self.fc = nn.Linear(hidden_size, 1)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        lstm_out, _ = self.lstm(x)
        predictions = self.fc(lstm_out[:, -1, :])
        return predictions


class ResourceForecaster:
    """资源需求预测器"""
    
    def __init__(self, model_path: str = None, seq_length: int = 7):
        self.seq_length = seq_length
        self.model = LSTMPredictor()
        
        if model_path and os.path.exists(model_path):
            self.model.load_state_dict(torch.load(model_path))
        
        self.model.eval()
    
    def predict(self, historical_data: List[List[float]]) -> float:
        """
        预测未来需求
        
        Args:
            historical_data: 历史数据序列，每个元素是特征向量
            
        Returns:
            预测值
        """
        # 准备输入
        if len(historical_data) < self.seq_length:
            # 数据不足，填充
            historical_data = [[0.0] * 5] * (self.seq_length - len(historical_data)) + historical_data
        
        input_seq = torch.FloatTensor(historical_data[-self.seq_length:]).unsqueeze(0)
        
        with torch.no_grad():
            prediction = self.model(input_seq)
        
        return float(prediction.item())
    
    def train(self, data: List[Tuple[List[List[float]], float]], epochs: int = 100):
        """训练模型"""
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
        
        for epoch in range(epochs):
            total_loss = 0
            for seq, target in data:
                optimizer.zero_grad()
                
                x = torch.FloatTensor(seq).unsqueeze(0)
                y = torch.FloatTensor([target])
                
                pred = self.model(x)
                loss = criterion(pred, y)
                
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
            
            if (epoch + 1) % 10 == 0:
                print(f"Epoch {epoch+1}, Loss: {total_loss/len(data):.4f}")
```

---

## 模型管理

**文件**: `core/model_manager.py`

```python
import os
import pickle
import hashlib
from typing import Any, Optional
from datetime import datetime
import json


class ModelManager:
    """模型管理器 - 负责模型的缓存、加载和版本管理"""
    
    def __init__(self, cache_dir: str = "models_cache"):
        self.cache_dir = cache_dir
        self.metadata_file = os.path.join(cache_dir, "metadata.json")
        
        os.makedirs(cache_dir, exist_ok=True)
        self.metadata = self._load_metadata()
    
    def save_model(self, name: str, model: Any, version: str = None) -> str:
        """
        保存模型
        
        Args:
            name: 模型名称
            model: 模型对象
            version: 版本号，不传则自动生成
            
        Returns:
            模型保存路径
        """
        version = version or datetime.now().strftime("%Y%m%d_%H%M%S")
        model_dir = os.path.join(self.cache_dir, name)
        os.makedirs(model_dir, exist_ok=True)
        
        model_path = os.path.join(model_dir, f"{version}.pkl")
        
        # 保存模型
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        # 计算模型哈希
        model_hash = self._compute_hash(model_path)
        
        # 更新元数据
        self.metadata[name] = {
            "latest_version": version,
            "versions": self.metadata.get(name, {}).get("versions", []) + [{
                "version": version,
                "path": model_path,
                "hash": model_hash,
                "created_at": datetime.now().isoformat()
            }]
        }
        self._save_metadata()
        
        return model_path
    
    def load_model(self, name: str, version: str = None) -> Optional[Any]:
        """
        加载模型
        
        Args:
            name: 模型名称
            version: 版本号，不传则加载最新版本
            
        Returns:
            模型对象
        """
        if name not in self.metadata:
            return None
        
        version = version or self.metadata[name]["latest_version"]
        
        # 查找版本
        for v in self.metadata[name]["versions"]:
            if v["version"] == version:
                with open(v["path"], 'rb') as f:
                    return pickle.load(f)
        
        return None
    
    def list_models(self) -> dict:
        """列出所有模型"""
        return self.metadata
    
    def _load_metadata(self) -> dict:
        """加载元数据"""
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_metadata(self):
        """保存元数据"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def _compute_hash(self, file_path: str) -> str:
        """计算文件哈希"""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
```

---

## 性能优化

### 1. 异步处理

```python
from fastapi import BackgroundTasks
import asyncio

@router.post("/clustering/async")
async def start_clustering_async(
    request: ClusteringRequest,
    background_tasks: BackgroundTasks
):
    """异步启动聚类任务"""
    task_id = generate_task_id()
    
    background_tasks.add_task(run_clustering_task, task_id, request)
    
    return {"task_id": task_id, "status": "pending"}


def run_clustering_task(task_id: str, request: ClusteringRequest):
    """后台执行聚类"""
    try:
        # 更新任务状态
        cache.set(f"task:{task_id}", {"status": "running"})
        
        # 执行聚类
        result = clustering_service.fit(request.data)
        
        # 保存结果
        cache.set(f"task:{task_id}", {
            "status": "completed",
            "result": result
        })
    except Exception as e:
        cache.set(f"task:{task_id}", {
            "status": "failed",
            "error": str(e)
        })
```

### 2. 模型缓存

```python
from functools import lru_cache
from core.model_manager import ModelManager

model_manager = ModelManager()

@lru_cache(maxsize=10)
def get_cached_model(model_name: str, version: str = None):
    """获取缓存的模型"""
    return model_manager.load_model(model_name, version)


# 预热常用模型
@app.on_event("startup")
async def preload_models():
    """服务启动时预加载模型"""
    models_to_preload = ["kmeans", "lstm", "nlp"]
    for model_name in models_to_preload:
        try:
            model = model_manager.load_model(model_name)
            if model:
                get_cached_model.cache_clear()
                get_cached_model(model_name)
                logger.info(f"预加载模型成功: {model_name}")
        except Exception as e:
            logger.warning(f"预加载模型失败: {model_name}, {e}")
```

### 3. 批处理

```python
@router.post("/nlp/batch")
async def analyze_sentiment_batch(texts: List[str]) -> List[Dict]:
    """批量情感分析"""
    analyzer = NLPSentimentAnalyzer()
    
    # 使用线程池并行处理
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(analyzer.analyze, texts))
    
    return results
```

---

## 测试

```python
# tests/test_algorithms.py
import pytest
import numpy as np
from src.algorithms.ahp import AHPCalculator


def test_ahp_calculate():
    """测试AHP计算"""
    calculator = AHPCalculator()
    
    scores = {
        "参与度": 85,
        "教育性": 90,
        "创新性": 75,
        "影响力": 80,
        "可持续性": 88
    }
    
    result = calculator.calculate(scores)
    
    assert 0 <= result.total_score <= 100
    assert result.consistency_check_passed
    assert len(result.dimension_scores) == 5


def test_ahp_invalid_score():
    """测试无效分数"""
    calculator = AHPCalculator()
    
    with pytest.raises(ValueError):
        calculator.calculate({"参与度": 150})  # 超出范围
```
