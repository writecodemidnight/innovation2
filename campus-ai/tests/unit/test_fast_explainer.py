# campus-ai/tests/unit/test_fast_explainer.py
import numpy as np
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.fast_explainer import FastExplainableClustering


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
