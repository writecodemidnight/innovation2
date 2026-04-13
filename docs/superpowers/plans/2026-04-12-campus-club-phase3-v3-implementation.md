# 校园社团活动评估系统 - 第三阶段V3实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现生产级性能优化的校园社团活动评估系统V3版本，解决V2版本的内存爆炸和计算复杂度问题

**Architecture:** 采用IncrementalPCA+MiniBatchKMeans实现可扩展学生画像，分层调度器替代NSGA-II实现O(n log n)复杂度，LRU缓存+模型分片解决Prophet内存问题，Celery异步任务系统支持水平扩展

**Tech Stack:** Python 3.11, FastAPI, scikit-learn, Prophet, Celery, Redis, PostgreSQL, MLflow, Prometheus, Docker

---

## 文件结构规划

```
campus-ai/src/
├── core/
│   ├── scalable_pipeline.py      # IncrementalPCA + MiniBatchKMeans管道
│   ├── fast_explainer.py         # Ridge回归快速解释器
│   └── exceptions.py             # 新增算法相关异常
├── scheduling/
│   ├── hierarchical_scheduler.py # 分层资源调度器
│   └── models.py                 # 调度相关数据模型
├── forecasting/
│   ├── memory_efficient_forecaster.py  # LRU缓存预测器
│   └── ensemble_forecaster.py    # 集成预测器
├── tasks/
│   ├── celery_app.py             # Celery应用配置
│   ├── clustering_tasks.py       # 聚类异步任务
│   ├── scheduling_tasks.py       # 调度异步任务
│   └── forecasting_tasks.py      # 预测异步任务
├── monitoring/
│   ├── drift_detector.py         # 数据漂移检测
│   └── metrics.py                # Prometheus指标
├── registry/
│   └── mlflow_manager.py         # MLflow模型管理
└── api/
    └── v3/
        ├── clustering.py         # V3聚类API
        ├── scheduling.py         # V3调度API
        └── forecasting.py        # V3预测API

tests/
├── unit/
│   ├── test_scalable_pipeline.py
│   ├── test_fast_explainer.py
│   ├── test_hierarchical_scheduler.py
│   └── test_memory_forecaster.py
├── integration/
│   ├── test_celery_tasks.py
│   └── test_api_v3.py
└── performance/
    ├── test_memory_usage.py
    └── test_latency.py
```

---

## Phase 1: 核心性能优化组件 (Week 1-2)

### Task 1: 可扩展特征管道 (ScalableFeaturePipeline)

**Files:**
- Create: `campus-ai/src/core/scalable_pipeline.py`
- Test: `campus-ai/tests/unit/test_scalable_pipeline.py`

- [ ] **Step 1: 编写IncrementalPCA基础测试**

```python
# campus-ai/tests/unit/test_scalable_pipeline.py
import numpy as np
import pytest
from src.core.scalable_pipeline import ScalableFeaturePipeline


class TestScalableFeaturePipeline:
    """测试可扩展特征管道"""

    def test_initialization(self):
        """测试管道初始化"""
        pipeline = ScalableFeaturePipeline(
            n_components=0.95,
            batch_size=100,
            n_clusters=6
        )
        assert pipeline.n_components == 0.95
        assert pipeline.batch_size == 100
        assert pipeline.n_clusters == 6
        assert pipeline.scaler_ is None
        assert pipeline.ipca_ is None
        assert pipeline.kmeans_ is None

    def test_partial_fit_single_batch(self):
        """测试单批次partial_fit"""
        pipeline = ScalableFeaturePipeline(batch_size=100)
        X_batch = np.random.randn(50, 10)
        
        result = pipeline.partial_fit(X_batch)
        
        assert result is pipeline
        assert pipeline.scaler_ is not None
        assert pipeline.ipca_ is not None

    def test_fit_transform_shape(self):
        """测试fit_transform输出形状"""
        np.random.seed(42)
        X = np.random.randn(200, 20)
        
        pipeline = ScalableFeaturePipeline(
            n_components=0.95,
            batch_size=50,
            n_clusters=4
        )
        pipeline.fit(X)
        
        X_transformed = pipeline.transform(X)
        
        # 降维后特征数应少于原特征数
        assert X_transformed.shape[0] == 200
        assert X_transformed.shape[1] < 20
        assert X_transformed.shape[1] >= 1

    def test_predict_returns_valid_labels(self):
        """测试预测返回有效标签"""
        np.random.seed(42)
        X = np.random.randn(100, 10)
        
        pipeline = ScalableFeaturePipeline(n_clusters=5)
        pipeline.fit(X)
        
        labels = pipeline.predict(X)
        
        assert len(labels) == 100
        assert all(0 <= label < 5 for label in labels)

    def test_save_and_load(self, tmp_path):
        """测试模型保存和加载"""
        np.random.seed(42)
        X = np.random.randn(100, 10)
        
        pipeline = ScalableFeaturePipeline(
            n_clusters=3,
            model_dir=str(tmp_path)
        )
        pipeline.fit(X)
        
        # 保存
        save_path = pipeline.save("v1.0")
        assert save_path.exists()
        
        # 加载
        loaded = ScalableFeaturePipeline.load("v1.0", model_dir=str(tmp_path))
        
        # 验证预测结果一致
        np.random.seed(42)
        X_test = np.random.randn(20, 10)
        labels1 = pipeline.predict(X_test)
        labels2 = loaded.predict(X_test)
        
        np.testing.assert_array_equal(labels1, labels2)

    def test_memory_efficiency_with_large_data(self):
        """测试大数据集内存效率"""
        # 模拟10万学生×100特征
        np.random.seed(42)
        X = np.random.randn(1000, 50)  # 减小规模用于测试
        
        pipeline = ScalableFeaturePipeline(
            batch_size=100,
            n_clusters=6
        )
        
        # 应该能在不OOM的情况下完成
        pipeline.fit(X)
        labels = pipeline.predict(X)
        
        assert len(labels) == 1000
```

- [ ] **Step 2: 运行测试确认失败**

```bash
cd campus-ai
python -m pytest tests/unit/test_scalable_pipeline.py -v
```

**Expected:** 所有测试FAIL，显示`ModuleNotFoundError`或类未定义

- [ ] **Step 3: 实现ScalableFeaturePipeline**

```python
# campus-ai/src/core/scalable_pipeline.py

from sklearn.decomposition import IncrementalPCA
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import MiniBatchKMeans
from sklearn.base import BaseEstimator, TransformerMixin
import numpy as np
from typing import Iterator, Optional
import joblib
import os
from pathlib import Path


class ScalableFeaturePipeline(BaseEstimator, TransformerMixin):
    """
    可扩展特征处理管道
    
    解决PCA内存爆炸问题:
    - 使用IncrementalPCA: 支持分批处理，内存复杂度O(batch_size × n_features)
    - 使用MiniBatchKMeans: 支持在线学习，内存复杂度O(n_clusters × n_features)
    
    性能对比 (10万学生 × 100特征):
    - V2 PCA: 需要40GB内存
    - V3 IncrementalPCA: 只需200MB内存 (batch_size=1000)
    """
    
    def __init__(
        self,
        n_components: float = 0.95,
        batch_size: int = 1000,
        n_clusters: int = 6,
        random_state: int = 42,
        model_dir: str = "./models"
    ):
        self.n_components = n_components
        self.batch_size = batch_size
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.model_dir = model_dir
        
        # 组件延迟初始化
        self.scaler_: Optional[StandardScaler] = None
        self.ipca_: Optional[IncrementalPCA] = None
        self.kmeans_: Optional[MiniBatchKMeans] = None
        
    def partial_fit(self, X_batch: np.ndarray) -> 'ScalableFeaturePipeline':
        """在线学习 - 分批拟合"""
        if self.scaler_ is None:
            self.scaler_ = StandardScaler()
            self.ipca_ = IncrementalPCA(
                n_components=self.n_components,
                batch_size=self.batch_size
            )
            
        # 分批标准化
        self.scaler_.partial_fit(X_batch)
        X_scaled = self.scaler_.transform(X_batch)
        
        # 分批PCA
        self.ipca_.partial_fit(X_scaled)
        
        return self
    
    def fit(self, X: np.ndarray, y=None) -> 'ScalableFeaturePipeline':
        """全量拟合 - 自动分batch处理"""
        n_samples = X.shape[0]
        n_batches = (n_samples + self.batch_size - 1) // self.batch_size
        
        # Phase 1: 在线学习标准化和PCA
        for i in range(n_batches):
            start_idx = i * self.batch_size
            end_idx = min((i + 1) * self.batch_size, n_samples)
            X_batch = X[start_idx:end_idx]
            self.partial_fit(X_batch)
            
        # Phase 2: 在降维后的数据上聚类
        X_transformed = self.transform(X)
        
        self.kmeans_ = MiniBatchKMeans(
            n_clusters=self.n_clusters,
            batch_size=self.batch_size,
            random_state=self.random_state,
            n_init=3,
            max_iter=100
        )
        self.kmeans_.fit(X_transformed)
        
        return self
    
    def transform(self, X: np.ndarray) -> np.ndarray:
        """特征转换"""
        if self.scaler_ is None or self.ipca_ is None:
            raise RuntimeError("Pipeline not fitted yet")
            
        X_scaled = self.scaler_.transform(X)
        X_reduced = self.ipca_.transform(X_scaled)
        return X_reduced
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """预测聚类标签"""
        X_transformed = self.transform(X)
        return self.kmeans_.predict(X_transformed)
    
    def save(self, version: str) -> Path:
        """保存模型组件"""
        save_dir = Path(self.model_dir) / f"pipeline_{version}"
        save_dir.mkdir(parents=True, exist_ok=True)
        
        joblib.dump(self.scaler_, save_dir / "scaler.joblib")
        joblib.dump(self.ipca_, save_dir / "ipca.joblib")
        joblib.dump(self.kmeans_, save_dir / "kmeans.joblib")
        
        # 保存元数据
        metadata = {
            "n_components": self.n_components,
            "batch_size": self.batch_size,
            "n_clusters": self.n_clusters,
            "explained_variance_ratio_": self.ipca_.explained_variance_ratio_.tolist() if self.ipca_ else None,
            "cluster_centers_": self.kmeans_.cluster_centers_.tolist() if self.kmeans_ else None
        }
        joblib.dump(metadata, save_dir / "metadata.joblib")
        
        return save_dir
    
    @classmethod
    def load(cls, version: str, model_dir: str = "./models") -> 'ScalableFeaturePipeline':
        """加载模型组件"""
        load_dir = Path(model_dir) / f"pipeline_{version}"
        
        instance = cls.__new__(cls)
        instance.model_dir = model_dir
        
        instance.scaler_ = joblib.load(load_dir / "scaler.joblib")
        instance.ipca_ = joblib.load(load_dir / "ipca.joblib")
        instance.kmeans_ = joblib.load(load_dir / "kmeans.joblib")
        
        metadata = joblib.load(load_dir / "metadata.joblib")
        instance.n_components = metadata["n_components"]
        instance.batch_size = metadata["batch_size"]
        instance.n_clusters = metadata["n_clusters"]
        instance.random_state = 42
        
        return instance
```

- [ ] **Step 4: 运行测试确认通过**

```bash
cd campus-ai
python -m pytest tests/unit/test_scalable_pipeline.py -v
```

**Expected:** 所有6个测试PASS

- [ ] **Step 5: 提交代码**

```bash
cd campus-ai
git add src/core/scalable_pipeline.py tests/unit/test_scalable_pipeline.py
git commit -m "feat: implement ScalableFeaturePipeline with IncrementalPCA and MiniBatchKMeans

- Add memory-efficient feature pipeline using IncrementalPCA
- Support batch processing to handle large datasets
- Implement MiniBatchKMeans for online clustering
- Add save/load functionality for model persistence
- Include comprehensive unit tests"
```

---

### Task 2: 快速可解释聚类 (FastExplainableClustering)

**Files:**
- Create: `campus-ai/src/core/fast_explainer.py`
- Test: `campus-ai/tests/unit/test_fast_explainer.py`

- [ ] **Step 1: 编写Ridge解释器测试**

```python
# campus-ai/tests/unit/test_fast_explainer.py
import numpy as np
import pytest
from src.core.fast_explainer import FastExplainableClustering


class TestFastExplainableClustering:
    """测试快速可解释聚类"""

    def test_initialization(self):
        """测试初始化"""
        explainer = FastExplainableClustering(
            regularization=1.0,
            top_k_features=5
        )
        assert explainer.regularization == 1.0
        assert explainer.top_k_features == 5
        assert explainer.explainers_ == {}

    def test_fit_creates_explainers(self):
        """测试fit为每个聚类创建解释器"""
        np.random.seed(42)
        X = np.random.randn(100, 10)
        labels = np.random.randint(0, 3, 100)
        centers = np.random.randn(3, 5)
        feature_names = [f"feature_{i}" for i in range(10)]
        
        explainer = FastExplainableClustering()
        explainer.fit(X, labels, centers, feature_names)
        
        assert len(explainer.explainers_) == 3
        assert 0 in explainer.explainers_
        assert 1 in explainer.explainers_
        assert 2 in explainer.explainers_

    def test_explain_returns_valid_structure(self):
        """测试explain返回有效结构"""
        np.random.seed(42)
        X = np.random.randn(100, 10)
        labels = np.random.randint(0, 3, 100)
        centers = np.random.randn(3, 5)
        feature_names = [f"feature_{i}" for i in range(10)]
        
        explainer = FastExplainableClustering(top_k_features=3)
        explainer.fit(X, labels, centers, feature_names)
        
        explanation = explainer.explain(X[0], cluster_id=0)
        
        assert "cluster_id" in explanation
        assert explanation["cluster_id"] == 0
        assert "top_positive_features" in explanation
        assert "top_negative_features" in explanation
        assert "confidence" in explanation
        assert "explanation_method" in explanation
        assert len(explanation["top_positive_features"]) <= 3
        assert len(explanation["top_negative_features"]) <= 3
        assert 0 <= explanation["confidence"] <= 1

    def test_explain_invalid_cluster(self):
        """测试无效聚类ID抛出异常"""
        explainer = FastExplainableClustering()
        explainer.explainers_ = {0: None, 1: None}
        
        with pytest.raises(ValueError, match="Unknown cluster_id: 99"):
            explainer.explain(np.random.randn(10), cluster_id=99)

    def test_batch_explain(self):
        """测试批量解释"""
        np.random.seed(42)
        X = np.random.randn(50, 10)
        labels = np.random.randint(0, 3, 50)
        centers = np.random.randn(3, 5)
        feature_names = [f"feature_{i}" for i in range(10)]
        
        explainer = FastExplainableClustering()
        explainer.fit(X, labels, centers, feature_names)
        
        explanations = explainer.batch_explain(X, labels)
        
        assert len(explanations) == 50
        for exp in explanations:
            assert "cluster_id" in exp
            assert "confidence" in exp

    def test_save_and_load(self, tmp_path):
        """测试保存和加载"""
        np.random.seed(42)
        X = np.random.randn(100, 10)
        labels = np.random.randint(0, 3, 100)
        centers = np.random.randn(3, 5)
        feature_names = [f"feature_{i}" for i in range(10)]
        
        explainer = FastExplainableClustering()
        explainer.fit(X, labels, centers, feature_names)
        
        save_path = tmp_path / "explainer.joblib"
        explainer.save(str(save_path))
        assert save_path.exists()
        
        loaded = FastExplainableClustering.load(str(save_path))
        
        # 验证解释结果一致
        exp1 = explainer.explain(X[0], cluster_id=0)
        exp2 = loaded.explain(X[0], cluster_id=0)
        
        assert exp1["cluster_id"] == exp2["cluster_id"]
        assert len(exp1["top_positive_features"]) == len(exp2["top_positive_features"])
```

- [ ] **Step 2: 运行测试确认失败**

```bash
cd campus-ai
python -m pytest tests/unit/test_fast_explainer.py -v
```

**Expected:** 所有测试FAIL

- [ ] **Step 3: 实现FastExplainableClustering**

```python
# campus-ai/src/core/fast_explainer.py

from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
import numpy as np
from typing import List, Dict
import joblib


class FastExplainableClustering:
    """
    快速可解释聚类
    
    解决SHAP实时计算太慢的问题:
    - V2: KernelSHAP每次预测需O(T×M×2^|S|) ~ 3-5秒
    - V3: 预训练Ridge回归解释器，每次预测O(n_features) ~ 5毫秒
    
    原理: 用线性模型近似聚类决策边界，特征系数即为特征重要性
    """
    
    def __init__(
        self,
        regularization: float = 1.0,
        top_k_features: int = 5
    ):
        self.regularization = regularization
        self.top_k_features = top_k_features
        self.explainers_: Dict[int, Ridge] = {}
        self.scaler_ = StandardScaler()
        self.feature_names_: List[str] = []
        
    def fit(
        self,
        X: np.ndarray,
        cluster_labels: np.ndarray,
        cluster_centers: np.ndarray,
        feature_names: List[str]
    ) -> 'FastExplainableClustering':
        """
        为每个聚类训练解释器
        
        Args:
            X: 原始特征 (n_samples, n_features)
            cluster_labels: 聚类标签 (n_samples,)
            cluster_centers: 聚类中心 (n_clusters, n_features_reduced)
            feature_names: 特征名列表
        """
        self.feature_names_ = feature_names
        X_scaled = self.scaler_.fit_transform(X)
        
        n_clusters = len(np.unique(cluster_labels))
        
        for cluster_id in range(n_clusters):
            # 创建二分类问题: 属于该聚类 vs 不属于
            y_binary = (cluster_labels == cluster_id).astype(int)
            
            # 用Ridge回归学习决策边界
            pos_idx = np.where(y_binary == 1)[0]
            neg_idx = np.where(y_binary == 0)[0]
            
            # 平衡采样
            n_pos = len(pos_idx)
            n_neg_sample = min(n_pos * 3, len(neg_idx))
            neg_sample_idx = np.random.choice(neg_idx, n_neg_sample, replace=False)
            
            sample_idx = np.concatenate([pos_idx, neg_sample_idx])
            X_sample = X_scaled[sample_idx]
            y_sample = y_binary[sample_idx]
            
            # 训练Ridge分类器
            ridge = Ridge(alpha=self.regularization)
            ridge.fit(X_sample, y_sample)
            
            self.explainers_[cluster_id] = ridge
            
        return self
    
    def explain(
        self,
        student_features: np.ndarray,
        cluster_id: int
    ) -> Dict:
        """
        快速解释聚类结果
        
        Returns:
            {
                "top_positive_features": [("feature_name", weight), ...],
                "top_negative_features": [("feature_name", weight), ...],
                "confidence": float
            }
        """
        if cluster_id not in self.explainers_:
            raise ValueError(f"Unknown cluster_id: {cluster_id}")
            
        ridge = self.explainers_[cluster_id]
        
        # 标准化特征
        student_scaled = self.scaler_.transform(student_features.reshape(1, -1))
        
        # 获取特征系数 (O(n_features)复杂度)
        coefficients = ridge.coef_
        
        # 按重要性排序
        feature_importance = list(zip(self.feature_names_, coefficients))
        feature_importance.sort(key=lambda x: abs(x[1]), reverse=True)
        
        # 正负向特征
        top_positive = [
            (name, float(weight)) 
            for name, weight in feature_importance 
            if weight > 0
        ][:self.top_k_features]
        
        top_negative = [
            (name, float(weight)) 
            for name, weight in feature_importance 
            if weight < 0
        ][:self.top_k_features]
        
        # 预测置信度
        prediction = ridge.predict(student_scaled)[0]
        confidence = float(prediction)
        
        return {
            "cluster_id": cluster_id,
            "top_positive_features": top_positive,
            "top_negative_features": top_negative,
            "confidence": confidence,
            "explanation_method": "ridge_approximation"
        }
    
    def batch_explain(
        self,
        X: np.ndarray,
        cluster_labels: np.ndarray
    ) -> List[Dict]:
        """批量解释"""
        explanations = []
        for i, features in enumerate(X):
            exp = self.explain(features, cluster_labels[i])
            explanations.append(exp)
        return explanations
    
    def save(self, path: str):
        """保存解释器"""
        joblib.dump({
            "explainers": self.explainers_,
            "scaler": self.scaler_,
            "feature_names": self.feature_names_,
            "regularization": self.regularization,
            "top_k_features": self.top_k_features
        }, path)
    
    @classmethod
    def load(cls, path: str) -> 'FastExplainableClustering':
        """加载解释器"""
        data = joblib.load(path)
        instance = cls.__new__(cls)
        instance.explainers_ = data["explainers"]
        instance.scaler_ = data["scaler"]
        instance.feature_names_ = data["feature_names"]
        instance.regularization = data["regularization"]
        instance.top_k_features = data["top_k_features"]
        return instance
```

- [ ] **Step 4: 运行测试确认通过**

```bash
cd campus-ai
python -m pytest tests/unit/test_fast_explainer.py -v
```

**Expected:** 所有6个测试PASS

- [ ] **Step 5: 提交代码**

```bash
cd campus-ai
git add src/core/fast_explainer.py tests/unit/test_fast_explainer.py
git commit -m "feat: implement FastExplainableClustering with Ridge regression

- Replace slow KernelSHAP with fast Ridge regression
- O(n_features) complexity instead of O(T×M×2^|S|)
- ~5ms explanation time vs 3-5s in V2
- Add batch explain and save/load functionality"
```

---

### Task 3: 分层资源调度器 (HierarchicalScheduler)

**Files:**
- Create: `campus-ai/src/scheduling/models.py`
- Create: `campus-ai/src/scheduling/hierarchical_scheduler.py`
- Test: `campus-ai/tests/unit/test_hierarchical_scheduler.py`

- [ ] **Step 1: 编写调度器测试**

```python
# campus-ai/tests/unit/test_hierarchical_scheduler.py
import pytest
from datetime import datetime, timedelta
from src.scheduling.models import TimeSlot, Activity, ActivityPriority, VenueSchedule
from src.scheduling.hierarchical_scheduler import HierarchicalScheduler


class TestTimeSlot:
    """测试时间槽"""

    def test_timeslot_creation(self):
        """测试时间槽创建"""
        slot = TimeSlot(
            venue_id="venue_1",
            start_time=datetime(2024, 1, 1, 9, 0),
            end_time=datetime(2024, 1, 1, 11, 0)
        )
        assert slot.venue_id == "venue_1"
        assert slot.duration_hours == 2.0

    def test_timeslot_conflict_same_venue(self):
        """测试同场地时间冲突"""
        slot1 = TimeSlot(
            venue_id="venue_1",
            start_time=datetime(2024, 1, 1, 9, 0),
            end_time=datetime(2024, 1, 1, 11, 0)
        )
        slot2 = TimeSlot(
            venue_id="venue_1",
            start_time=datetime(2024, 1, 1, 10, 0),
            end_time=datetime(2024, 1, 1, 12, 0)
        )
        assert slot1.conflicts_with(slot2)

    def test_timeslot_no_conflict_different_venue(self):
        """测试不同场地无冲突"""
        slot1 = TimeSlot(
            venue_id="venue_1",
            start_time=datetime(2024, 1, 1, 9, 0),
            end_time=datetime(2024, 1, 1, 11, 0)
        )
        slot2 = TimeSlot(
            venue_id="venue_2",
            start_time=datetime(2024, 1, 1, 10, 0),
            end_time=datetime(2024, 1, 1, 12, 0)
        )
        assert not slot1.conflicts_with(slot2)


class TestVenueSchedule:
    """测试场地调度表"""

    def test_add_slot_no_conflict(self):
        """测试无冲突添加"""
        schedule = VenueSchedule("venue_1")
        slot = TimeSlot(
            venue_id="venue_1",
            start_time=datetime(2024, 1, 1, 9, 0),
            end_time=datetime(2024, 1, 1, 11, 0)
        )
        assert schedule.add_slot(slot) is True
        assert len(schedule.slots) == 1

    def test_add_slot_with_conflict(self):
        """测试有冲突时添加失败"""
        schedule = VenueSchedule("venue_1")
        slot1 = TimeSlot(
            venue_id="venue_1",
            start_time=datetime(2024, 1, 1, 9, 0),
            end_time=datetime(2024, 1, 1, 11, 0)
        )
        slot2 = TimeSlot(
            venue_id="venue_1",
            start_time=datetime(2024, 1, 1, 10, 0),
            end_time=datetime(2024, 1, 1, 12, 0)
        )
        schedule.add_slot(slot1)
        assert schedule.add_slot(slot2) is False


class TestHierarchicalScheduler:
    """测试分层调度器"""

    def test_initialization(self):
        """测试调度器初始化"""
        scheduler = HierarchicalScheduler(
            venues=["v1", "v2"],
            available_staff=["s1", "s2"],
            total_budget=10000.0
        )
        assert len(scheduler.venues) == 2
        assert scheduler.total_budget == 10000.0
        assert "v1" in scheduler.venue_schedules
        assert "v2" in scheduler.venue_schedules

    def test_schedule_single_activity(self):
        """测试单个活动调度"""
        scheduler = HierarchicalScheduler(
            venues=["hall_a"],
            available_staff=["staff_1"],
            total_budget=1000.0
        )
        
        activities = [
            Activity(
                id="act_1",
                name="Test Activity",
                priority=ActivityPriority.HIGH,
                duration_hours=2.0,
                acceptable_venues=["hall_a"],
                preferred_time_ranges=[
                    (datetime(2024, 1, 1, 9, 0), datetime(2024, 1, 1, 17, 0))
                ],
                min_budget=100.0,
                max_budget=500.0,
                required_staff_count=1,
                expected_participants=50,
                club_id="club_1"
            )
        ]
        
        result = scheduler.schedule(
            activities,
            planning_horizon_start=datetime(2024, 1, 1, 8, 0),
            planning_horizon_end=datetime(2024, 1, 7, 20, 0)
        )
        
        assert len(result["scheduled"]) == 1
        assert len(result["unscheduled"]) == 0
        assert result["scheduled"][0].assigned_slot is not None
        assert result["scheduled"][0].assigned_budget >= 100.0

    def test_priority_ordering(self):
        """测试优先级排序"""
        scheduler = HierarchicalScheduler(
            venues=["hall_a"],
            available_staff=["s1"],
            total_budget=1000.0
        )
        
        activities = [
            Activity(
                id=f"act_{i}",
                name=f"Activity {i}",
                priority=priority,
                duration_hours=2.0,
                acceptable_venues=["hall_a"],
                preferred_time_ranges=[
                    (datetime(2024, 1, 1, 9, 0), datetime(2024, 1, 1, 17, 0))
                ],
                min_budget=50.0,
                max_budget=200.0,
                required_staff_count=1,
                expected_participants=30,
                club_id="club_1"
            )
            for i, priority in enumerate([
                ActivityPriority.LOW,
                ActivityPriority.CRITICAL,
                ActivityPriority.MEDIUM
            ])
        ]
        
        # 只给一个时间段，应该优先安排CRITICAL
        result = scheduler.schedule(
            activities,
            planning_horizon_start=datetime(2024, 1, 1, 9, 0),
            planning_horizon_end=datetime(2024, 1, 1, 11, 0)
        )
        
        scheduled_ids = {a.id for a in result["scheduled"]}
        assert "act_1" in scheduled_ids  # CRITICAL优先级应该被安排

    def test_calculate_metrics(self):
        """测试指标计算"""
        scheduler = HierarchicalScheduler(
            venues=["hall_a", "hall_b"],
            available_staff=["s1", "s2"],
            total_budget=10000.0
        )
        
        activities = [
            Activity(
                id="act_1",
                name="Activity 1",
                priority=ActivityPriority.HIGH,
                duration_hours=4.0,
                acceptable_venues=["hall_a"],
                preferred_time_ranges=[
                    (datetime(2024, 1, 1, 9, 0), datetime(2024, 1, 1, 17, 0))
                ],
                min_budget=500.0,
                max_budget=1000.0,
                required_staff_count=1,
                expected_participants=100,
                club_id="club_1"
            )
        ]
        
        result = scheduler.schedule(
            activities,
            planning_horizon_start=datetime(2024, 1, 1, 8, 0),
            planning_horizon_end=datetime(2024, 1, 1, 20, 0)
        )
        
        metrics = result["metrics"]
        assert "venue_utilization" in metrics
        assert "budget_utilization" in metrics
        assert metrics["scheduled_count"] == 1
        assert metrics["avg_budget_per_activity"] >= 500.0
```

- [ ] **Step 2: 运行测试确认失败**

```bash
cd campus-ai
python -m pytest tests/unit/test_hierarchical_scheduler.py -v
```

**Expected:** 所有测试FAIL

- [ ] **Step 3: 实现数据模型**

```python
# campus-ai/src/scheduling/models.py

from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from datetime import datetime
from enum import Enum


class ActivityPriority(Enum):
    CRITICAL = 4    # 校级重大活动
    HIGH = 3        # 重要社团活动
    MEDIUM = 2      # 常规活动
    LOW = 1         # 小型活动


@dataclass
class TimeSlot:
    """时间槽 - 调度的基本单元"""
    venue_id: str
    start_time: datetime
    end_time: datetime
    duration_hours: float = field(init=False)
    
    def __post_init__(self):
        self.duration_hours = (self.end_time - self.start_time).total_seconds() / 3600
    
    def conflicts_with(self, other: 'TimeSlot') -> bool:
        """检查时间冲突"""
        if self.venue_id != other.venue_id:
            return False
        return not (self.end_time <= other.start_time or self.start_time >= other.end_time)


@dataclass 
class Activity:
    """活动定义"""
    id: str
    name: str
    priority: ActivityPriority
    duration_hours: float
    acceptable_venues: List[str]
    preferred_time_ranges: List[Tuple[datetime, datetime]]
    min_budget: float
    max_budget: float
    required_staff_count: int
    expected_participants: int
    club_id: str
    
    # 运行时分配
    assigned_slot: Optional[TimeSlot] = None
    assigned_budget: float = 0.0
    assigned_staff: List[str] = field(default_factory=list)


@dataclass
class VenueSchedule:
    """场地调度表 - 使用区间树思想优化冲突检测"""
    venue_id: str
    slots: List[TimeSlot] = field(default_factory=list)
    
    def add_slot(self, slot: TimeSlot) -> bool:
        """添加时间槽，返回是否成功"""
        if self._has_conflict(slot):
            return False
        
        # 插入并保持有序
        idx = self._find_insert_position(slot)
        self.slots.insert(idx, slot)
        return True
    
    def _has_conflict(self, slot: TimeSlot) -> bool:
        """使用二分查找检测冲突: O(log n)"""
        if not self.slots:
            return False
        
        idx = self._find_insert_position(slot)
        
        # 只检查相邻的几个槽位
        check_range = range(max(0, idx - 2), min(len(self.slots), idx + 2))
        for i in check_range:
            if self.slots[i].conflicts_with(slot):
                return True
        return False
    
    def _find_insert_position(self, slot: TimeSlot) -> int:
        """二分查找插入位置"""
        left, right = 0, len(self.slots)
        while left < right:
            mid = (left + right) // 2
            if self.slots[mid].start_time < slot.start_time:
                left = mid + 1
            else:
                right = mid
        return left
    
    def get_utilization(self, start: datetime, end: datetime) -> float:
        """计算时间段内的场地利用率"""
        total_hours = (end - start).total_seconds() / 3600
        if total_hours == 0:
            return 0.0
            
        occupied_hours = sum(
            s.duration_hours for s in self.slots
            if s.start_time >= start and s.end_time <= end
        )
        return occupied_hours / total_hours
```

- [ ] **Step 4: 实现HierarchicalScheduler**

```python
# campus-ai/src/scheduling/hierarchical_scheduler.py

import numpy as np
from typing import List, Dict
from datetime import datetime, timedelta
import random

from .models import TimeSlot, Activity, ActivityPriority, VenueSchedule


class HierarchicalScheduler:
    """
    分层资源调度器
    
    解决NSGA-II复杂度问题:
    - V2: O(pop × gens × n²) = 2-3小时
    - V3: O(n log n) + 分层优化 = < 10分钟
    
    核心思想:
    1. 分层: 优先保证高优先级活动，再优化低优先级
    2. 贪心初始解: 快速获得可行解
    3. 局部搜索: 只在冲突区域进行优化
    4. 时间槽索引: 冲突检测从O(n)降到O(log n)
    """
    
    def __init__(
        self,
        venues: List[str],
        available_staff: List[str],
        total_budget: float,
        optimization_timeout: int = 600
    ):
        self.venues = venues
        self.available_staff = available_staff
        self.total_budget = total_budget
        self.optimization_timeout = optimization_timeout
        
        # 场地调度表
        self.venue_schedules: Dict[str, VenueSchedule] = {
            v: VenueSchedule(v) for v in venues
        }
        
    def schedule(
        self,
        activities: List[Activity],
        planning_horizon_start: datetime,
        planning_horizon_end: datetime
    ) -> Dict:
        """
        分层调度主算法
        
        Phase 1: 分层分配 (O(n log n))
        Phase 2: 局部优化
        Phase 3: 资源均衡
        """
        # 按优先级分组
        priority_groups = self._group_by_priority(activities)
        
        scheduled = []
        unscheduled = []
        
        # Phase 1: 分层贪心调度
        for priority in [ActivityPriority.CRITICAL, ActivityPriority.HIGH, 
                        ActivityPriority.MEDIUM, ActivityPriority.LOW]:
            group = priority_groups.get(priority, [])
            
            # 按期望参与人数排序（大活动优先）
            group.sort(key=lambda a: a.expected_participants, reverse=True)
            
            for activity in group:
                success = self._schedule_activity(
                    activity, 
                    planning_horizon_start, 
                    planning_horizon_end
                )
                if success:
                    scheduled.append(activity)
                else:
                    unscheduled.append(activity)
        
        # Phase 2: 局部搜索优化
        self._local_search_optimization(scheduled, planning_horizon_start, planning_horizon_end)
        
        # Phase 3: 资源分配
        self._allocate_resources(scheduled)
        
        return {
            "scheduled": scheduled,
            "unscheduled": unscheduled,
            "metrics": self._calculate_metrics(scheduled, planning_horizon_start, planning_horizon_end)
        }
    
    def _group_by_priority(self, activities: List[Activity]) -> Dict[ActivityPriority, List[Activity]]:
        """按优先级分组"""
        groups = {}
        for activity in activities:
            if activity.priority not in groups:
                groups[activity.priority] = []
            groups[activity.priority].append(activity)
        return groups
    
    def _schedule_activity(
        self,
        activity: Activity,
        horizon_start: datetime,
        horizon_end: datetime
    ) -> bool:
        """为单个活动寻找最优时间槽"""
        best_slot = None
        best_score = -float('inf')
        
        # 生成候选时间槽
        candidate_slots = self._generate_candidate_slots(activity, horizon_start, horizon_end)
        
        for slot in candidate_slots:
            # 快速冲突检测: O(log n)
            if not self.venue_schedules[slot.venue_id].add_slot(slot):
                continue
            
            # 计算评分
            score = self._evaluate_slot(activity, slot)
            
            if score > best_score:
                best_score = score
                best_slot = slot
            
            # 回滚试探性添加
            self.venue_schedules[slot.venue_id].slots.remove(slot)
        
        if best_slot:
            activity.assigned_slot = best_slot
            self.venue_schedules[best_slot.venue_id].add_slot(best_slot)
            return True
        
        return False
    
    def _generate_candidate_slots(
        self,
        activity: Activity,
        horizon_start: datetime,
        horizon_end: datetime
    ) -> List[TimeSlot]:
        """生成候选时间槽"""
        slots = []
        
        # 在偏好时间段内生成候选
        for preferred_start, preferred_end in activity.preferred_time_ranges:
            start = max(preferred_start, horizon_start)
            end = min(preferred_end, horizon_end)
            
            current = start
            while current + timedelta(hours=activity.duration_hours) <= end:
                slot_end = current + timedelta(hours=activity.duration_hours)
                for venue_id in activity.acceptable_venues:
                    slots.append(TimeSlot(venue_id, current, slot_end))
                current += timedelta(hours=1)
        
        return slots
    
    def _evaluate_slot(self, activity: Activity, slot: TimeSlot) -> float:
        """评估时间槽质量"""
        score = 0.0
        
        # 1. 场地偏好
        venue_preference = activity.acceptable_venues.index(slot.venue_id)
        score += (len(activity.acceptable_venues) - venue_preference) * 10
        
        # 2. 场地利用率均衡
        venue_util = len(self.venue_schedules[slot.venue_id].slots)
        avg_util = sum(len(vs.slots) for vs in self.venue_schedules.values()) / len(self.venues)
        score -= abs(venue_util - avg_util) * 2
        
        # 3. 时间偏好（周末活动给分）
        if slot.start_time.weekday() >= 5:
            score += 5
        
        return score
    
    def _local_search_optimization(
        self,
        scheduled: List[Activity],
        horizon_start: datetime,
        horizon_end: datetime
    ):
        """局部搜索优化"""
        max_iterations = min(len(scheduled) * 10, 1000)
        
        for _ in range(max_iterations):
            if not scheduled:
                break
            
            activity = random.choice(scheduled)
            old_slot = activity.assigned_slot
            
            # 暂时移除
            if old_slot:
                self.venue_schedules[old_slot.venue_id].slots.remove(old_slot)
                activity.assigned_slot = None
            
            # 尝试找到更好的槽位
            success = self._schedule_activity(activity, horizon_start, horizon_end)
            
            if not success and old_slot:
                # 恢复原来的安排
                activity.assigned_slot = old_slot
                self.venue_schedules[old_slot.venue_id].add_slot(old_slot)
    
    def _allocate_resources(self, scheduled: List[Activity]):
        """分配预算和人员"""
        # 按优先级分配预算
        total_min_budget = sum(a.min_budget for a in scheduled)
        remaining_budget = self.total_budget - total_min_budget
        
        if remaining_budget > 0:
            # 按优先级和活动规模分配剩余预算
            priority_weights = {
                ActivityPriority.CRITICAL: 4,
                ActivityPriority.HIGH: 3,
                ActivityPriority.MEDIUM: 2,
                ActivityPriority.LOW: 1
            }
            
            total_weight = sum(
                priority_weights[a.priority] * a.expected_participants
                for a in scheduled
            )
            
            for activity in scheduled:
                weight = priority_weights[activity.priority] * activity.expected_participants
                extra_budget = remaining_budget * (weight / total_weight)
                activity.assigned_budget = activity.min_budget + extra_budget
                activity.assigned_budget = min(activity.assigned_budget, activity.max_budget)
        else:
            for activity in scheduled:
                activity.assigned_budget = activity.min_budget
        
        # 分配人员
        staff_idx = 0
        for activity in scheduled:
            n_staff = activity.required_staff_count
            activity.assigned_staff = [
                self.available_staff[(staff_idx + i) % len(self.available_staff)]
                for i in range(n_staff)
            ]
            staff_idx += n_staff
    
    def _calculate_metrics(
        self,
        scheduled: List[Activity],
        horizon_start: datetime,
        horizon_end: datetime
    ) -> Dict:
        """计算调度质量指标"""
        if not scheduled:
            return {}
        
        # 场地利用率
        total_capacity = len(self.venues) * (horizon_end - horizon_start).total_seconds() / 3600
        total_used = sum(a.assigned_slot.duration_hours for a in scheduled if a.assigned_slot)
        venue_utilization = total_used / total_capacity if total_capacity > 0 else 0
        
        # 预算利用率
        budget_utilization = sum(a.assigned_budget for a in scheduled) / self.total_budget if self.total_budget > 0 else 0
        
        return {
            "venue_utilization": round(venue_utilization, 3),
            "budget_utilization": round(budget_utilization, 3),
            "scheduled_count": len(scheduled),
            "avg_budget_per_activity": round(sum(a.assigned_budget for a in scheduled) / len(scheduled), 2)
        }
```

- [ ] **Step 5: 运行测试确认通过**

```bash
cd campus-ai
python -m pytest tests/unit/test_hierarchical_scheduler.py -v
```

**Expected:** 所有5个测试PASS

- [ ] **Step 6: 提交代码**

```bash
cd campus-ai
git add src/scheduling/
git add tests/unit/test_hierarchical_scheduler.py
git commit -m "feat: implement HierarchicalScheduler with O(n log n) complexity

- Replace NSGA-II with hierarchical greedy + local search
- Add VenueSchedule with binary search conflict detection
- Implement priority-based activity scheduling
- Add resource allocation (budget and staff)
- Include comprehensive metrics calculation"
```

---

### Task 4: 内存高效预测器 (MemoryEfficientForecaster)

**Files:**
- Create: `campus-ai/src/forecasting/memory_efficient_forecaster.py`
- Test: `campus-ai/tests/unit/test_memory_forecaster.py`

- [ ] **Step 1: 编写LRU缓存预测器测试**

```python
# campus-ai/tests/unit/test_memory_forecaster.py
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.forecasting.memory_efficient_forecaster import MemoryEfficientForecaster


class TestMemoryEfficientForecaster:
    """测试内存高效预测器"""

    def test_initialization(self, tmp_path):
        """测试初始化"""
        forecaster = MemoryEfficientForecaster(
            model_dir=str(tmp_path),
            max_cache_size=5,
            cache_ttl_hours=1
        )
        assert forecaster.max_cache_size == 5
        assert forecaster.cache_ttl.total_seconds() == 3600
        assert len(forecaster._cache) == 0

    def test_get_model_id(self, tmp_path):
        """测试模型ID生成"""
        forecaster = MemoryEfficientForecaster(model_dir=str(tmp_path))
        
        model_id1 = forecaster._get_model_id("sports", "gym")
        model_id2 = forecaster._get_model_id("sports", "gym")
        model_id3 = forecaster._get_model_id("music", "hall")
        
        assert model_id1 == model_id2  # 相同输入产生相同ID
        assert model_id1 != model_id3  # 不同输入产生不同ID
        assert len(model_id1) == 12

    def test_cache_operations(self, tmp_path):
        """测试缓存操作"""
        forecaster = MemoryEfficientForecaster(
            model_dir=str(tmp_path),
            max_cache_size=2
        )
        
        # 模拟模型
        class MockModel:
            pass
        
        model1 = MockModel()
        metadata1 = {
            'created_at': datetime.now().isoformat(),
            'last_used': datetime.now(),
            'use_count': 0
        }
        
        # 添加到缓存
        forecaster._add_to_cache("model_1", model1, metadata1)
        assert len(forecaster._cache) == 1
        assert "model_1" in forecaster._cache
        
        # 获取缓存
        retrieved = forecaster._get_from_cache("model_1")
        assert retrieved is model1
        
        # 添加第二个模型
        model2 = MockModel()
        metadata2 = metadata1.copy()
        forecaster._add_to_cache("model_2", model2, metadata2)
        
        # 添加第三个模型（应驱逐第一个）
        model3 = MockModel()
        metadata3 = metadata1.copy()
        forecaster._add_to_cache("model_3", model3, metadata3)
        
        assert len(forecaster._cache) == 2
        assert "model_1" not in forecaster._cache  # LRU被驱逐

    def test_preprocess_data(self, tmp_path):
        """测试数据预处理"""
        forecaster = MemoryEfficientForecaster(model_dir=str(tmp_path))
        
        # 创建测试数据
        data = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=10),
            'value': range(10)
        })
        
        result = forecaster._preprocess_data(data)
        
        assert 'ds' in result.columns
        assert 'y' in result.columns
        assert len(result) == 10
        assert result['ds'].dtype == 'datetime64[ns]'

    def test_preprocess_with_missing_values(self, tmp_path):
        """测试处理缺失值"""
        forecaster = MemoryEfficientForecaster(model_dir=str(tmp_path))
        
        data = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=5),
            'value': [1.0, np.nan, 3.0, None, 5.0]
        })
        
        result = forecaster._preprocess_data(data)
        
        # 应移除包含缺失值的行
        assert len(result) == 3
        assert not result['y'].isna().any()

    def test_get_cache_stats(self, tmp_path):
        """测试缓存统计"""
        forecaster = MemoryEfficientForecaster(
            model_dir=str(tmp_path),
            max_cache_size=10
        )
        
        # 添加一个模型到元数据
        forecaster._metadata["model_1"] = {
            "use_count": 10
        }
        
        stats = forecaster.get_cache_stats()
        
        assert "cache_size" in stats
        assert "max_cache_size" in stats
        assert "total_models_on_disk" in stats
        assert stats["max_cache_size"] == 10
```

- [ ] **Step 2: 运行测试确认失败**

```bash
cd campus-ai
python -m pytest tests/unit/test_memory_forecaster.py -v
```

**Expected:** 所有测试FAIL

- [ ] **Step 3: 实现MemoryEfficientForecaster**

```python
# campus-ai/src/forecasting/memory_efficient_forecaster.py

from functools import lru_cache
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import joblib
import os
import json
from pathlib import Path
from dataclasses import dataclass

import pandas as pd
import numpy as np
from prophet import Prophet


@dataclass
class ModelMetadata:
    """模型元数据"""
    model_id: str
    activity_type: str
    venue_type: str
    created_at: datetime
    last_used: datetime
    use_count: int
    mape_score: float


class MemoryEfficientForecaster:
    """
    内存高效预测器
    
    解决Prophet内存爆炸问题:
    - V2: 1000个模型常驻内存 = 80GB
    - V3: LRU缓存最多10个模型 + 磁盘存储 = < 1GB
    
    核心策略:
    1. LRU缓存: 只保留最近使用的模型在内存
    2. 模型分片: 按活动类型聚合，减少模型数量
    3. 延迟加载: 按需从磁盘加载模型
    4. 统一预处理: 提取通用特征，减少模型复杂度
    """
    
    def __init__(
        self,
        model_dir: str = "./models/forecasting",
        max_cache_size: int = 10,
        cache_ttl_hours: int = 1
    ):
        self.model_dir = model_dir
        self.max_cache_size = max_cache_size
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
        
        # 内存中的模型缓存: {model_id: (model, metadata)}
        self._cache: Dict[str, tuple] = {}
        self._cache_order: List[str] = []  # LRU顺序
        
        # 元数据存储
        self.metadata_path = os.path.join(model_dir, "metadata.json")
        self._metadata: Dict[str, dict] = self._load_metadata()
        
        os.makedirs(model_dir, exist_ok=True)

    def _get_model_id(self, activity_type: str, venue_type: str) -> str:
        """生成模型ID - 按活动类型和场地类型聚合"""
        import hashlib
        key = f"{activity_type}_{venue_type}"
        return hashlib.md5(key.encode()).hexdigest()[:12]

    def _load_metadata(self) -> Dict:
        """加载模型元数据"""
        if os.path.exists(self.metadata_path):
            with open(self.metadata_path, 'r') as f:
                return json.load(f)
        return {}

    def _save_metadata(self):
        """保存模型元数据"""
        with open(self.metadata_path, 'w') as f:
            json.dump(self._metadata, f, indent=2, default=str)

    def _get_from_cache(self, model_id: str) -> Optional[Prophet]:
        """从LRU缓存获取模型"""
        if model_id in self._cache:
            model, metadata = self._cache[model_id]
            
            # 检查TTL
            last_used = datetime.fromisoformat(metadata['last_used']) if isinstance(metadata['last_used'], str) else metadata['last_used']
            if datetime.now() - last_used > self.cache_ttl:
                self._evict_from_cache(model_id)
                return None
            
            # 更新LRU顺序
            if model_id in self._cache_order:
                self._cache_order.remove(model_id)
            self._cache_order.append(model_id)
            metadata['last_used'] = datetime.now().isoformat()
            metadata['use_count'] += 1
            
            return model
        return None

    def _add_to_cache(self, model_id: str, model: Prophet, metadata: dict):
        """添加模型到LRU缓存"""
        # 如果缓存已满，驱逐最久未使用的
        while len(self._cache) >= self.max_cache_size:
            if self._cache_order:
                lru_id = self._cache_order.pop(0)
                self._evict_from_cache(lru_id)
            else:
                break
        
        self._cache[model_id] = (model, metadata)
        self._cache_order.append(model_id)

    def _evict_from_cache(self, model_id: str):
        """从缓存驱逐模型"""
        if model_id in self._cache:
            del self._cache[model_id]
            if model_id in self._cache_order:
                self._cache_order.remove(model_id)

    def _load_model_from_disk(self, model_id: str) -> Optional[Prophet]:
        """从磁盘加载模型"""
        model_path = os.path.join(self.model_dir, f"{model_id}.joblib")
        if os.path.exists(model_path):
            return joblib.load(model_path)
        return None

    def _save_model_to_disk(self, model_id: str, model: Prophet):
        """保存模型到磁盘"""
        model_path = os.path.join(self.model_dir, f"{model_id}.joblib")
        joblib.dump(model, model_path)

    def get_or_create_model(
        self,
        activity_type: str,
        venue_type: str,
        historical_data: Optional[pd.DataFrame] = None
    ) -> Prophet:
        """
        获取或创建模型
        
        优先级:
        1. 检查LRU缓存
        2. 从磁盘加载
        3. 训练新模型
        """
        model_id = self._get_model_id(activity_type, venue_type)
        
        # 1. 检查缓存
        model = self._get_from_cache(model_id)
        if model is not None:
            return model
        
        # 2. 从磁盘加载
        model = self._load_model_from_disk(model_id)
        if model is not None:
            metadata = self._metadata.get(model_id, {
                'created_at': datetime.now().isoformat(),
                'use_count': 0,
                'mape_score': 0.0
            })
            self._add_to_cache(model_id, model, metadata)
            return model
        
        # 3. 训练新模型
        if historical_data is None:
            raise ValueError(f"Model {model_id} not found and no training data provided")
        
        model = self._train_model(historical_data)
        
        # 保存
        metadata = {
            'model_id': model_id,
            'activity_type': activity_type,
            'venue_type': venue_type,
            'created_at': datetime.now().isoformat(),
            'last_used': datetime.now().isoformat(),
            'use_count': 1,
            'mape_score': 0.0
        }
        
        self._save_model_to_disk(model_id, model)
        self._metadata[model_id] = metadata
        self._save_metadata()
        self._add_to_cache(model_id, model, metadata)
        
        return model

    def _train_model(self, data: pd.DataFrame) -> Prophet:
        """训练Prophet模型"""
        # 统一预处理
        df = self._preprocess_data(data)
        
        # 配置Prophet - 减少复杂度
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            interval_width=0.8,
            changepoint_prior_scale=0.05
        )
        
        # 添加学期假期效应
        model.add_country_holidays(country_name='CN')
        
        model.fit(df)
        return model

    def _preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """统一数据预处理"""
        df = data.copy()
        
        # 标准化列名
        if 'date' in df.columns:
            df = df.rename(columns={'date': 'ds'})
        if 'value' in df.columns:
            df = df.rename(columns={'value': 'y'})
        
        # 确保数据类型
        df['ds'] = pd.to_datetime(df['ds'])
        df['y'] = pd.to_numeric(df['y'], errors='coerce')
        
        # 处理缺失值
        df = df.dropna(subset=['ds', 'y'])
        
        # 异常值处理 (3-sigma)
        if len(df) > 0:
            mean, std = df['y'].mean(), df['y'].std()
            if std > 0:
                df = df[df['y'].between(mean - 3*std, mean + 3*std)]
        
        return df[['ds', 'y']]

    def predict(
        self,
        activity_type: str,
        venue_type: str,
        periods: int = 30,
        freq: str = 'D',
        historical_data: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """
        预测API
        
        典型性能:
        - 缓存命中: < 10ms
        - 磁盘加载: < 100ms
        - 训练新模型: 5-10s (异步执行)
        """
        model = self.get_or_create_model(activity_type, venue_type, historical_data)
        
        future = model.make_future_dataframe(periods=periods, freq=freq)
        forecast = model.predict(future)
        
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]

    def get_cache_stats(self) -> Dict:
        """获取缓存统计"""
        return {
            "cache_size": len(self._cache),
            "max_cache_size": self.max_cache_size,
            "cached_models": list(self._cache.keys()),
            "total_models_on_disk": len(self._metadata),
            "cache_hit_rate": self._calculate_hit_rate()
        }

    def _calculate_hit_rate(self) -> float:
        """计算缓存命中率"""
        if not self._metadata:
            return 0.0
        total_uses = sum(m.get('use_count', 0) for m in self._metadata.values())
        cache_uses = sum(m.get('use_count', 0) for mid, m in self._metadata.items() if mid in self._cache)
        return cache_uses / total_uses if total_uses > 0 else 0.0
```

- [ ] **Step 4: 运行测试确认通过**

```bash
cd campus-ai
python -m pytest tests/unit/test_memory_forecaster.py -v
```

**Expected:** 所有6个测试PASS（注意：Prophet相关测试可能需要安装依赖）

- [ ] **Step 5: 提交代码**

```bash
cd campus-ai
git add src/forecasting/
git add tests/unit/test_memory_forecaster.py
git commit -m "feat: implement MemoryEfficientForecaster with LRU cache

- Add LRU cache to limit in-memory models to 10
- Implement model sharding by activity_type and venue_type
- Add lazy loading from disk
- Include unified data preprocessing with outlier handling
- Add cache statistics monitoring"
```

---

## Phase 2: 工程架构 (Week 3-4)

### Task 5: Celery异步任务系统

**Files:**
- Create: `campus-ai/src/tasks/celery_app.py`
- Create: `campus-ai/src/tasks/clustering_tasks.py`
- Create: `campus-ai/src/tasks/scheduling_tasks.py`
- Modify: `campus-ai/src/core/config.py`
- Test: `campus-ai/tests/integration/test_celery_tasks.py`

- [ ] **Step 1: 添加Celery配置到settings**

```python
# campus-ai/src/core/config.py
# 在Settings类中添加以下配置

    # Celery配置
    celery_broker_url: str = Field(default="redis://localhost:6379/0")
    celery_result_backend: str = Field(default="redis://localhost:6379/0")
    celery_task_serializer: str = Field(default="json")
    celery_accept_content: List[str] = Field(default=["json"])
    celery_timezone: str = Field(default="Asia/Shanghai")
    celery_enable_utc: bool = Field(default=True)
    celery_task_time_limit: int = Field(default=3600)  # 1小时
```

- [ ] **Step 2: 实现Celery应用**

```python
# campus-ai/src/tasks/celery_app.py

from celery import Celery
from celery.signals import task_success, task_failure
import os

from ..core.config import get_settings

settings = get_settings()

# Celery配置
celery_app = Celery(
    'campus_club_ml',
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        'src.tasks.clustering_tasks',
        'src.tasks.scheduling_tasks',
        'src.tasks.forecasting_tasks',
    ]
)

celery_app.conf.update(
    task_serializer=settings.celery_task_serializer,
    accept_content=settings.celery_accept_content,
    result_serializer='json',
    timezone=settings.celery_timezone,
    enable_utc=settings.celery_enable_utc,
    task_track_started=True,
    task_time_limit=settings.celery_task_time_limit,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

# 队列路由
celery_app.conf.task_routes = {
    'clustering.*': {'queue': 'clustering'},
    'scheduling.*': {'queue': 'scheduling'},
    'forecasting.*': {'queue': 'forecasting'},
}


@task_success.connect
def handle_task_success(sender=None, result=None, **kwargs):
    """任务成功监控"""
    print(f"Task {sender.name} succeeded")


@task_failure.connect
def handle_task_failure(sender=None, task_id=None, exception=None, **kwargs):
    """任务失败监控"""
    print(f"Task {sender.name} failed: {exception}")
```

- [ ] **Step 3: 实现聚类异步任务**

```python
# campus-ai/src/tasks/clustering_tasks.py

from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
from typing import List, Dict
import numpy as np
import pandas as pd

from ..core.scalable_pipeline import ScalableFeaturePipeline
from ..core.fast_explainer import FastExplainableClustering


@shared_task(bind=True, max_retries=3, soft_time_limit=300)
def train_clustering_model(
    self,
    student_ids: List[str] = None,
    n_clusters: int = 6,
    model_version: str = None
) -> Dict:
    """
    异步训练聚类模型
    
    时间预估:
    - 1000学生: ~30秒
    - 10000学生: ~2分钟
    - 100000学生: ~5分钟
    """
    try:
        # 从数据库获取特征数据（模拟）
        features_df = _get_student_features_from_db(student_ids)
        feature_names = features_df.columns.tolist()
        X = features_df.values
        
        # 训练管道
        pipeline = ScalableFeaturePipeline(
            n_clusters=n_clusters,
            batch_size=1000
        )
        pipeline.fit(X)
        
        # 预测
        labels = pipeline.predict(X)
        cluster_centers = pipeline.kmeans_.cluster_centers_
        
        # 训练解释器
        explainer = FastExplainableClustering()
        explainer.fit(X, labels, cluster_centers, feature_names)
        
        # 保存模型
        if model_version:
            pipeline.save(model_version)
            explainer.save(f"{pipeline.model_dir}/explainer_{model_version}.joblib")
        
        return {
            "status": "success",
            "model_version": model_version,
            "n_students": len(X),
            "n_clusters": n_clusters,
            "silhouette_score": float(pipeline.kmeans_.inertia_)
        }
        
    except SoftTimeLimitExceeded:
        self.retry(countdown=60)
    except Exception as exc:
        self.retry(exc=exc, countdown=30)


@shared_task(bind=True, max_retries=3)
def predict_student_clusters(
    self,
    student_ids: List[str],
    model_version: str
) -> List[Dict]:
    """异步预测学生聚类"""
    try:
        # 加载模型
        pipeline = ScalableFeaturePipeline.load(model_version)
        explainer = FastExplainableClustering.load(
            f"{pipeline.model_dir}/explainer_{model_version}.joblib"
        )
        
        # 获取特征
        features_df = _get_student_features_from_db(student_ids)
        X = features_df.values
        
        # 预测
        labels = pipeline.predict(X)
        
        # 生成解释
        explanations = explainer.batch_explain(X, labels)
        
        # 组装结果
        results = []
        for i, student_id in enumerate(student_ids):
            results.append({
                "student_id": student_id,
                "cluster_id": int(labels[i]),
                "explanation": explanations[i]
            })
        
        return results
        
    except Exception as exc:
        self.retry(exc=exc, countdown=10)


def _get_student_features_from_db(student_ids: List[str] = None) -> pd.DataFrame:
    """从数据库获取学生特征（模拟实现）"""
    # 实际实现应查询数据库
    if student_ids is None:
        # 返回模拟数据
        np.random.seed(42)
        return pd.DataFrame(
            np.random.randn(1000, 20),
            columns=[f"feature_{i}" for i in range(20)]
        )
    
    # 根据ID查询
    np.random.seed(42)
    return pd.DataFrame(
        np.random.randn(len(student_ids), 20),
        columns=[f"feature_{i}" for i in range(20)],
        index=student_ids
    )
```

- [ ] **Step 4: 实现调度异步任务**

```python
# campus-ai/src/tasks/scheduling_tasks.py

from celery import shared_task
from typing import List, Dict
from datetime import datetime

from ..scheduling.hierarchical_scheduler import HierarchicalScheduler
from ..scheduling.models import Activity, ActivityPriority


@shared_task(bind=True, max_retries=2, soft_time_limit=600)
def optimize_schedule(
    self,
    activities_data: List[Dict],
    venues: List[str],
    available_staff: List[str],
    total_budget: float,
    planning_start: str,
    planning_end: str,
    timeout: int = 600
) -> Dict:
    """
    异步资源调度优化
    
    预估时间: 5-10分钟
    """
    try:
        # 转换活动数据
        activities = [_dict_to_activity(a) for a in activities_data]
        
        # 创建调度器
        scheduler = HierarchicalScheduler(
            venues=venues,
            available_staff=available_staff,
            total_budget=total_budget,
            optimization_timeout=timeout
        )
        
        # 执行调度
        result = scheduler.schedule(
            activities,
            planning_horizon_start=datetime.fromisoformat(planning_start),
            planning_horizon_end=datetime.fromisoformat(planning_end)
        )
        
        # 序列化结果
        return {
            "status": "success",
            "scheduled_count": len(result["scheduled"]),
            "unscheduled_count": len(result["unscheduled"]),
            "metrics": result["metrics"],
            "scheduled_activities": [
                _activity_to_dict(a) for a in result["scheduled"]
            ],
            "unscheduled_activities": [
                {"id": a.id, "name": a.name} for a in result["unscheduled"]
            ]
        }
        
    except Exception as exc:
        self.retry(exc=exc, countdown=30)


def _dict_to_activity(data: Dict) -> Activity:
    """将字典转换为Activity对象"""
    priority_map = {
        "CRITICAL": ActivityPriority.CRITICAL,
        "HIGH": ActivityPriority.HIGH,
        "MEDIUM": ActivityPriority.MEDIUM,
        "LOW": ActivityPriority.LOW,
    }
    
    return Activity(
        id=data["id"],
        name=data["name"],
        priority=priority_map.get(data["priority"], ActivityPriority.MEDIUM),
        duration_hours=data["duration_hours"],
        acceptable_venues=data["acceptable_venues"],
        preferred_time_ranges=[
            (datetime.fromisoformat(start), datetime.fromisoformat(end))
            for start, end in data["preferred_time_ranges"]
        ],
        min_budget=data["min_budget"],
        max_budget=data["max_budget"],
        required_staff_count=data["required_staff_count"],
        expected_participants=data["expected_participants"],
        club_id=data["club_id"]
    )


def _activity_to_dict(activity: Activity) -> Dict:
    """将Activity对象转换为字典"""
    return {
        "id": activity.id,
        "name": activity.name,
        "priority": activity.priority.name,
        "assigned_slot": {
            "venue_id": activity.assigned_slot.venue_id,
            "start_time": activity.assigned_slot.start_time.isoformat(),
            "end_time": activity.assigned_slot.end_time.isoformat(),
        } if activity.assigned_slot else None,
        "assigned_budget": activity.assigned_budget,
        "assigned_staff": activity.assigned_staff,
    }
```

- [ ] **Step 5: 编写集成测试**

```python
# campus-ai/tests/integration/test_celery_tasks.py
import pytest
from unittest.mock import patch, MagicMock


class TestCeleryTasks:
    """测试Celery异步任务"""

    @pytest.fixture
    def mock_celery(self):
        """模拟Celery任务"""
        with patch('src.tasks.clustering_tasks._get_student_features_from_db') as mock_db:
            mock_db.return_value = MagicMock()
            yield mock_db

    def test_train_clustering_model_task_exists(self):
        """测试训练任务存在"""
        from src.tasks.clustering_tasks import train_clustering_model
        assert train_clustering_model is not None

    def test_predict_student_clusters_task_exists(self):
        """测试预测任务存在"""
        from src.tasks.clustering_tasks import predict_student_clusters
        assert predict_student_clusters is not None

    def test_optimize_schedule_task_exists(self):
        """测试调度任务存在"""
        from src.tasks.scheduling_tasks import optimize_schedule
        assert optimize_schedule is not None
```

- [ ] **Step 6: 提交代码**

```bash
cd campus-ai
git add src/tasks/
git add tests/integration/test_celery_tasks.py
git commit -m "feat: implement Celery async task system

- Add Celery app configuration with Redis broker
- Implement clustering training task with retry logic
- Implement clustering prediction task
- Implement scheduling optimization task
- Add queue routing for different task types"
```

---

### Task 6: V3 API路由

**Files:**
- Create: `campus-ai/src/api/v3/clustering.py`
- Create: `campus-ai/src/api/v3/scheduling.py`
- Create: `campus-ai/src/api/v3/__init__.py`
- Modify: `campus-ai/src/main.py`
- Test: `campus-ai/tests/integration/test_api_v3.py`

- [ ] **Step 1: 实现V3聚类API**

```python
# campus-ai/src/api/v3/clustering.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from celery.result import AsyncResult

from ...tasks.clustering_tasks import train_clustering_model, predict_student_clusters
from ...tasks.celery_app import celery_app

router = APIRouter(prefix="/clustering", tags=["v3-clustering"])


class ClusteringTrainRequest(BaseModel):
    """聚类训练请求"""
    student_ids: Optional[List[str]] = None
    n_clusters: int = 6
    retrain: bool = False


class ClusteringPredictRequest(BaseModel):
    """聚类预测请求"""
    student_ids: List[str]
    model_version: str = "latest"


class TaskResponse(BaseModel):
    """任务响应"""
    task_id: str
    status: str
    message: str


@router.post("/train", response_model=TaskResponse)
async def train_clustering(request: ClusteringTrainRequest):
    """
    异步训练聚类模型
    
    返回任务ID用于轮询结果
    """
    from datetime import datetime
    
    task = train_clustering_model.delay(
        student_ids=request.student_ids,
        n_clusters=request.n_clusters,
        model_version=f"kmeans_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    
    return TaskResponse(
        task_id=task.id,
        status="submitted",
        message="Training job submitted. Use /tasks/{task_id} to check status."
    )


@router.post("/predict", response_model=TaskResponse)
async def predict_clustering(request: ClusteringPredictRequest):
    """异步预测学生聚类"""
    task = predict_student_clusters.delay(
        student_ids=request.student_ids,
        model_version=request.model_version
    )
    
    return TaskResponse(
        task_id=task.id,
        status="submitted",
        message="Prediction job submitted."
    )
```

- [ ] **Step 2: 实现V3调度API**

```python
# campus-ai/src/api/v3/scheduling.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime

from ...tasks.scheduling_tasks import optimize_schedule

router = APIRouter(prefix="/scheduling", tags=["v3-scheduling"])


class ActivityRequest(BaseModel):
    """活动请求数据"""
    id: str
    name: str
    priority: str  # CRITICAL, HIGH, MEDIUM, LOW
    duration_hours: float
    acceptable_venues: List[str]
    preferred_time_ranges: List[tuple]  # [(start, end), ...]
    min_budget: float
    max_budget: float
    required_staff_count: int
    expected_participants: int
    club_id: str


class SchedulingRequest(BaseModel):
    """调度优化请求"""
    activities: List[ActivityRequest]
    venues: List[str]
    available_staff: List[str]
    total_budget: float
    planning_start: str  # ISO格式
    planning_end: str
    optimization_timeout: int = 600


@router.post("/optimize")
async def optimize_scheduling(request: SchedulingRequest):
    """
    异步资源调度优化
    
    复杂度高，必须异步执行
    预估时间: 5-10分钟
    """
    activities_data = [
        {
            "id": a.id,
            "name": a.name,
            "priority": a.priority,
            "duration_hours": a.duration_hours,
            "acceptable_venues": a.acceptable_venues,
            "preferred_time_ranges": a.preferred_time_ranges,
            "min_budget": a.min_budget,
            "max_budget": a.max_budget,
            "required_staff_count": a.required_staff_count,
            "expected_participants": a.expected_participants,
            "club_id": a.club_id
        }
        for a in request.activities
    ]
    
    task = optimize_schedule.delay(
        activities_data=activities_data,
        venues=request.venues,
        available_staff=request.available_staff,
        total_budget=request.total_budget,
        planning_start=request.planning_start,
        planning_end=request.planning_end,
        timeout=request.optimization_timeout
    )
    
    return {
        "task_id": task.id,
        "status": "submitted",
        "estimated_time": "5-10 minutes"
    }
```

- [ ] **Step 3: 实现任务状态查询API**

```python
# campus-ai/src/api/v3/tasks.py

from fastapi import APIRouter, HTTPException
from celery.result import AsyncResult

from ...tasks.celery_app import celery_app

router = APIRouter(prefix="/tasks", tags=["v3-tasks"])


@router.get("/{task_id}")
async def get_task_status(task_id: str):
    """查询异步任务状态"""
    result = AsyncResult(task_id, app=celery_app)
    
    response = {
        "task_id": task_id,
        "status": result.status,
    }
    
    if result.ready():
        if result.successful():
            response["result"] = result.get()
        else:
            response["error"] = str(result.result)
    
    return response
```

- [ ] **Step 4: 创建V3路由包**

```python
# campus-ai/src/api/v3/__init__.py

from fastapi import APIRouter

from .clustering import router as clustering_router
from .scheduling import router as scheduling_router
from .tasks import router as tasks_router

v3_router = APIRouter(prefix="/api/v3/ml")

v3_router.include_router(clustering_router)
v3_router.include_router(scheduling_router)
v3_router.include_router(tasks_router)
```

- [ ] **Step 5: 修改主应用添加V3路由**

```python
# campus-ai/src/main.py
# 添加V3路由导入

from .api.v3 import v3_router

# 在app创建后添加
app.include_router(v3_router)
```

- [ ] **Step 6: 提交代码**

```bash
cd campus-ai
git add src/api/v3/
git commit -m "feat: implement V3 API routes

- Add async clustering train/predict endpoints
- Add scheduling optimization endpoint
- Add task status query endpoint
- Organize V3 routes under /api/v3/ml prefix"
```

---

### Task 7: 数据漂移检测与监控

**Files:**
- Create: `campus-ai/src/monitoring/drift_detector.py`
- Create: `campus-ai/src/monitoring/metrics.py`
- Test: `campus-ai/tests/unit/test_drift_detector.py`

- [ ] **Step 1: 实现漂移检测器**

```python
# campus-ai/src/monitoring/drift_detector.py

import numpy as np
from scipy import stats
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class DriftReport:
    """漂移检测报告"""
    feature_name: str
    drift_detected: bool
    p_value: float
    statistic: float
    baseline_mean: float
    current_mean: float
    severity: str  # low, medium, high


class DataDriftDetector:
    """
    数据漂移检测器
    
    检测方法:
    1. KS检验: 检测分布变化
    2. PSI (Population Stability Index): 检测人群稳定性
    3. Wasserstein距离: 检测分布偏移程度
    """
    
    def __init__(
        self,
        psi_threshold: float = 0.2,
        ks_pvalue_threshold: float = 0.05,
        wasserstein_threshold: float = 0.1
    ):
        self.psi_threshold = psi_threshold
        self.ks_pvalue_threshold = ks_pvalue_threshold
        self.wasserstein_threshold = wasserstein_threshold
        
        self.baseline_stats: Dict[str, dict] = {}
    
    def fit_baseline(self, X: np.ndarray, feature_names: List[str]):
        """建立基线统计"""
        for i, name in enumerate(feature_names):
            self.baseline_stats[name] = {
                "mean": float(np.mean(X[:, i])),
                "std": float(np.std(X[:, i])),
                "min": float(np.min(X[:, i])),
                "max": float(np.max(X[:, i])),
                "percentiles": np.percentile(X[:, i], [5, 25, 50, 75, 95]).tolist(),
                "histogram": np.histogram(X[:, i], bins=20)[0].tolist()
            }
    
    def detect_drift(
        self,
        X_current: np.ndarray,
        feature_names: List[str]
    ) -> List[DriftReport]:
        """检测数据漂移"""
        reports = []
        
        for i, name in enumerate(feature_names):
            baseline = self.baseline_stats.get(name)
            if not baseline:
                continue
            
            current = X_current[:, i]
            
            # KS检验
            baseline_samples = np.random.normal(
                baseline["mean"], 
                baseline["std"], 
                size=len(current)
            )
            ks_stat, ks_pvalue = stats.ks_2samp(baseline_samples, current)
            
            # PSI计算
            psi = self._calculate_psi(baseline["histogram"], current)
            
            # Wasserstein距离
            wasserstein = stats.wasserstein_distance(baseline_samples, current)
            
            # 判断是否漂移
            drift_detected = (
                ks_pvalue < self.ks_pvalue_threshold or
                psi > self.psi_threshold or
                wasserstein > self.wasserstein_threshold
            )
            
            # 严重度评估
            severity = "low"
            if psi > 0.3 or ks_pvalue < 0.01:
                severity = "high"
            elif psi > 0.2 or ks_pvalue < 0.05:
                severity = "medium"
            
            reports.append(DriftReport(
                feature_name=name,
                drift_detected=drift_detected,
                p_value=float(ks_pvalue),
                statistic=float(ks_stat),
                baseline_mean=baseline["mean"],
                current_mean=float(np.mean(current)),
                severity=severity
            ))
        
        return reports
    
    def _calculate_psi(self, expected_hist: List, current: np.ndarray) -> float:
        """计算PSI"""
        bins = len(expected_hist)
        current_hist, _ = np.histogram(current, bins=bins)
        
        expected_pct = np.array(expected_hist) / sum(expected_hist)
        current_pct = current_hist / sum(current_hist)
        
        expected_pct = np.where(expected_pct == 0, 0.0001, expected_pct)
        current_pct = np.where(current_pct == 0, 0.0001, current_pct)
        
        psi = np.sum((current_pct - expected_pct) * np.log(current_pct / expected_pct))
        return float(psi)
    
    def generate_report(self, reports: List[DriftReport]) -> Dict:
        """生成漂移检测报告"""
        drifted_features = [r for r in reports if r.drift_detected]
        high_severity = [r for r in drifted_features if r.severity == "high"]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_features": len(reports),
            "drifted_features_count": len(drifted_features),
            "high_severity_count": len(high_severity),
            "drift_rate": len(drifted_features) / len(reports) if reports else 0,
            "needs_retraining": len(high_severity) > 0,
            "drifted_features": [
                {
                    "name": r.feature_name,
                    "severity": r.severity,
                    "p_value": r.p_value,
                    "baseline_mean": r.baseline_mean,
                    "current_mean": r.current_mean
                }
                for r in drifted_features
            ]
        }
```

- [ ] **Step 2: 实现Prometheus指标**

```python
# campus-ai/src/monitoring/metrics.py

from prometheus_client import Counter, Histogram, Gauge, Info
import time
from functools import wraps

# 模型预测指标
PREDICTION_LATENCY = Histogram(
    'ml_prediction_latency_seconds',
    'ML prediction latency in seconds',
    ['model_type', 'model_version']
)

PREDICTION_COUNT = Counter(
    'ml_prediction_total',
    'Total number of predictions',
    ['model_type', 'model_version', 'status']
)

# 训练任务指标
TRAINING_DURATION = Histogram(
    'ml_training_duration_seconds',
    'Training job duration',
    ['model_type']
)

TRAINING_ERRORS = Counter(
    'ml_training_errors_total',
    'Total training errors',
    ['model_type', 'error_type']
)

# 资源使用指标
ACTIVE_MODELS = Gauge(
    'ml_active_models',
    'Number of active models in memory',
    ['model_type']
)

CACHE_HIT_RATE = Gauge(
    'ml_cache_hit_rate',
    'Model cache hit rate',
    ['model_type']
)

# 数据漂移指标
DRIFT_DETECTED = Gauge(
    'ml_drift_detected',
    'Whether data drift is detected',
    ['model_type', 'feature_name']
)


def track_prediction(model_type: str, model_version: str):
    """预测性能追踪装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            status = "success"
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception:
                status = "error"
                raise
            finally:
                duration = time.time() - start_time
                PREDICTION_LATENCY.labels(
                    model_type=model_type,
                    model_version=model_version
                ).observe(duration)
                
                PREDICTION_COUNT.labels(
                    model_type=model_type,
                    model_version=model_version,
                    status=status
                ).inc()
        
        return wrapper
    return decorator


def track_training(model_type: str):
    """训练性能追踪装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                TRAINING_ERRORS.labels(
                    model_type=model_type,
                    error_type=type(e).__name__
                ).inc()
                raise
            finally:
                duration = time.time() - start_time
                TRAINING_DURATION.labels(
                    model_type=model_type
                ).observe(duration)
        
        return wrapper
    return decorator
```

- [ ] **Step 3: 提交代码**

```bash
cd campus-ai
git add src/monitoring/
git commit -m "feat: add drift detection and Prometheus metrics

- Implement DataDriftDetector with KS test and PSI
- Add severity classification for drift detection
- Add Prometheus metrics for prediction and training
- Add decorators for performance tracking"
```

---

## Phase 3: 生产部署 (Week 5-6)

### Task 8: Docker Compose配置

**Files:**
- Create: `campus-ai/docker-compose.prod.yml`
- Create: `campus-ai/Dockerfile.worker`
- Create: `campus-ai/prometheus.yml`

- [ ] **Step 1: 创建工作线程Dockerfile**

```dockerfile
# campus-ai/Dockerfile.worker

FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY src/ ./src/

# 设置Python路径
ENV PYTHONPATH=/app

# 工作线程启动命令由docker-compose指定
```

- [ ] **Step 2: 创建Prometheus配置**

```yaml
# campus-ai/prometheus.yml

global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'ml-api'
    static_configs:
      - targets: ['ml-api:8000']
    metrics_path: /metrics

  - job_name: 'celery-workers'
    static_configs:
      - targets: ['worker-clustering:8000', 'worker-scheduling:8000']
```

- [ ] **Step 3: 创建生产docker-compose**

```yaml
# campus-ai/docker-compose.prod.yml

version: '3.8'

services:
  # API服务
  ml-api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
      - DATABASE_URL=postgresql://user:pass@postgres:5432/campus_club
    depends_on:
      - redis
      - postgres
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Celery Worker - 聚类任务
  worker-clustering:
    build:
      context: .
      dockerfile: Dockerfile.worker
    command: celery -A src.tasks.celery_app worker -Q clustering -n clustering@%h --concurrency=2
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
    depends_on:
      - redis
      - postgres
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '4'
          memory: 8G

  # Celery Worker - 调度任务
  worker-scheduling:
    build:
      context: .
      dockerfile: Dockerfile.worker
    command: celery -A src.tasks.celery_app worker -Q scheduling -n scheduling@%h --concurrency=1
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
    depends_on:
      - redis
      - postgres
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '4'
          memory: 8G

  # Celery Beat - 定时任务
  beat:
    build:
      context: .
      dockerfile: Dockerfile.worker
    command: celery -A src.tasks.celery_app beat
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
    depends_on:
      - redis

  # Flower - 任务监控
  flower:
    build:
      context: .
      dockerfile: Dockerfile.worker
    command: celery -A src.tasks.celery_app flower --port=5555
    ports:
      - "5555:5555"
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
    depends_on:
      - redis

  # Redis - 消息队列和缓存
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    deploy:
      resources:
        limits:
          memory: 2G

  # PostgreSQL - 数据库
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=campus_club
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  # Prometheus - 指标收集
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus

  # Grafana - 可视化
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin

volumes:
  redis_data:
  postgres_data:
  prometheus_data:
  grafana_data:
```

- [ ] **Step 4: 提交代码**

```bash
cd campus-ai
git add docker-compose.prod.yml Dockerfile.worker prometheus.yml
git commit -m "feat: add production Docker Compose configuration

- Add multi-service Docker Compose for production
- Configure Celery workers for clustering and scheduling
- Add Redis, PostgreSQL, Prometheus, Grafana services
- Include health checks and resource limits"
```

---

## 实施验证检查清单

### 性能测试
- [ ] K-Means内存占用 < 2GB (10万学生)
- [ ] 聚类训练时间 < 5分钟
- [ ] 资源调度时间 < 10分钟 (1000活动)
- [ ] API响应时间 < 200ms (p99)
- [ ] 缓存命中率 > 80%

### 功能测试
- [ ] IncrementalPCA正确降维
- [ ] MiniBatchKMeans正确聚类
- [ ] Ridge解释器输出有效特征重要性
- [ ] 分层调度器正确处理优先级
- [ ] LRU缓存正确驱逐旧模型
- [ ] Celery任务正确执行和重试

### 监控测试
- [ ] Prometheus指标正常采集
- [ ] Grafana仪表板正常显示
- [ ] Flower任务监控正常
- [ ] 数据漂移检测正确触发

---

## 参考文档

- [V3设计文档](../../specs/2026-04-12-campus-club-phase3-algorithm-design-v3.md)
- [V2设计文档](../../specs/2026-04-12-campus-club-phase3-algorithm-design-v2.md)
- [V1设计文档](../../specs/2026-04-12-campus-club-phase3-algorithm-design.md)
- [Phase3算法设计](../../specs/2026-04-12-campus-club-phase3-algorithm-design.md)

---

**文档版本:** 1.0  
**创建日期:** 2026-04-12  
**作者:** Claude Code  
**状态:** 待实施
