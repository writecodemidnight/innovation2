# campus-ai/tests/unit/test_memory_forecaster.py
import pytest
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from forecasting.memory_efficient_forecaster import MemoryEfficientForecaster


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
        assert 'datetime64' in str(result['ds'].dtype)

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
