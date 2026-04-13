# campus-ai/tests/unit/test_scalable_pipeline.py
import numpy as np
import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.scalable_pipeline import ScalableFeaturePipeline


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
