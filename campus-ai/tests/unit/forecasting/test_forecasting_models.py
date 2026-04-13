"""
预测模型测试 (ARIMA, LSTM, Random Forest)
"""

import pytest
import numpy as np
import pandas as pd
import os
import tempfile

from src.forecasting.models.arima_forecaster import ARIMAForecaster
from src.forecasting.models.lstm_forecaster import LSTMForecaster
from src.forecasting.models.random_forest_forecaster import (
    RandomForestForecaster,
    FeatureEngineer
)


class TestARIMAForecaster:
    """测试ARIMA预测器"""

    def test_init(self):
        """测试初始化"""
        forecaster = ARIMAForecaster(order=(2, 1, 2))

        assert forecaster.order == (2, 1, 2)
        assert forecaster.auto_select is True
        assert forecaster.fitted is False

    def test_create_sample_data(self):
        """创建测试数据"""
        np.random.seed(42)
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        values = np.cumsum(np.random.randn(100)) + 100

        return pd.Series(values, index=dates)

    def test_fit(self):
        """测试训练"""
        data = self.test_create_sample_data()
        forecaster = ARIMAForecaster(auto_select=False, order=(1, 1, 1))

        forecaster.fit(data)

        assert forecaster.fitted is True
        assert forecaster.data is not None

    def test_predict(self):
        """测试预测"""
        data = self.test_create_sample_data()
        forecaster = ARIMAForecaster(auto_select=False, order=(1, 1, 1))
        forecaster.fit(data)

        result = forecaster.predict(steps=30)

        assert len(result.forecast) == 30
        assert isinstance(result.aic, float)
        assert isinstance(result.bic, float)

    def test_evaluate(self):
        """测试评估"""
        data = self.test_create_sample_data()
        train_data = data[:80]
        test_data = data[80:]

        forecaster = ARIMAForecaster(auto_select=False, order=(1, 1, 1))
        forecaster.fit(train_data)

        metrics = forecaster.evaluate(test_data)

        assert metrics.mae >= 0
        assert metrics.rmse >= 0
        assert metrics.mape >= 0

    def test_cross_validate(self):
        """测试交叉验证"""
        data = self.test_create_sample_data()
        forecaster = ARIMAForecaster(auto_select=False, order=(1, 1, 1))
        forecaster.fit(data)

        cv_results = forecaster.cross_validate(n_splits=3)

        assert 'mae_mean' in cv_results
        assert 'rmse_mean' in cv_results
        assert 'mape_mean' in cv_results

    def test_forecast_resource_needs(self):
        """测试资源需求预测接口"""
        data = self.test_create_sample_data()
        forecaster = ARIMAForecaster(auto_select=False, order=(1, 1, 1))
        forecaster.fit(data)

        result = forecaster.forecast_resource_needs(
            planning_horizon_days=30,
            resource_type="participants"
        )

        assert result['resource_type'] == "participants"
        assert result['planning_horizon_days'] == 30
        assert 'forecast' in result
        assert 'statistics' in result
        assert 'model_info' in result


class TestLSTMForecaster:
    """测试LSTM预测器"""

    def test_init(self):
        """测试初始化"""
        forecaster = LSTMForecaster(
            seq_length=30,
            hidden_size=64,
            epochs=50
        )

        assert forecaster.seq_length == 30
        assert forecaster.hidden_size == 64
        assert forecaster.epochs == 50
        assert forecaster.fitted is False

    def test_create_sample_data(self):
        """创建测试数据"""
        np.random.seed(42)
        dates = pd.date_range(start='2023-01-01', periods=200, freq='D')
        values = np.sin(np.linspace(0, 4*np.pi, 200)) * 10 + 100 + np.random.randn(200) * 2

        return pd.Series(values, index=dates)

    def test_fit(self):
        """测试训练"""
        data = self.test_create_sample_data()
        forecaster = LSTMForecaster(seq_length=30, epochs=5)

        forecaster.fit(data, validation_split=0.2)

        assert forecaster.fitted is True

    def test_predict(self):
        """测试预测"""
        data = self.test_create_sample_data()
        forecaster = LSTMForecaster(seq_length=30, epochs=5)
        forecaster.fit(data)

        last_seq = data.values[:30]
        result = forecaster.predict(steps=30, last_sequence=last_seq)

        assert len(result.forecast) == 30

    def test_evaluate(self):
        """测试评估"""
        data = self.test_create_sample_data()
        train_data = data[:150]
        test_data = data[150:]

        forecaster = LSTMForecaster(seq_length=30, epochs=5)
        forecaster.fit(train_data)

        metrics = forecaster.evaluate(test_data)

        assert metrics.mae >= 0
        assert metrics.rmse >= 0
        assert metrics.epochs_trained > 0


class TestRandomForestForecaster:
    """测试随机森林预测器"""

    def test_init(self):
        """测试初始化"""
        forecaster = RandomForestForecaster(
            n_estimators=50,
            max_depth=10
        )

        assert forecaster.n_estimators == 50
        assert forecaster.max_depth == 10
        assert forecaster.fitted is False

    def test_create_sample_data(self):
        """创建测试数据"""
        np.random.seed(42)
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        values = np.cumsum(np.random.randn(100)) + 100

        return pd.Series(values, index=dates)

    def test_fit(self):
        """测试训练"""
        data = self.test_create_sample_data()
        forecaster = RandomForestForecaster(n_estimators=10)

        forecaster.fit(data)

        assert forecaster.fitted is True
        assert forecaster.feature_names is not None

    def test_predict(self):
        """测试预测"""
        data = self.test_create_sample_data()
        forecaster = RandomForestForecaster(n_estimators=10)
        forecaster.fit(data)

        # 准备特征用于预测
        features = forecaster.feature_engineer.extract_features(data)
        result = forecaster.predict(steps=30, last_features=features)

        assert len(result.forecast) == 30

    def test_evaluate(self):
        """测试评估"""
        data = self.test_create_sample_data()
        train_data = data[:80]
        test_data = data[80:]

        forecaster = RandomForestForecaster(n_estimators=10)
        forecaster.fit(train_data)

        metrics = forecaster.evaluate(test_data)

        assert metrics.mae >= 0
        assert metrics.rmse >= 0
        assert isinstance(metrics.feature_importance, dict)

    def test_get_feature_importance(self):
        """测试获取特征重要性"""
        data = self.test_create_sample_data()
        forecaster = RandomForestForecaster(n_estimators=10)
        forecaster.fit(data)

        importance = forecaster.get_feature_importance(top_n=5)

        assert len(importance) <= 5

    def test_explain_prediction(self):
        """测试预测解释"""
        data = self.test_create_sample_data()
        forecaster = RandomForestForecaster(n_estimators=10)
        forecaster.fit(data)

        features = forecaster.feature_engineer.extract_features(data)
        explanation = forecaster.explain_prediction(features[:1])

        assert "method" in explanation


class TestFeatureEngineer:
    """测试特征工程"""

    def test_extract_features(self):
        """测试特征提取"""
        np.random.seed(42)
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        values = np.random.randn(100).cumsum() + 100
        data = pd.Series(values, index=dates)

        features = FeatureEngineer.extract_features(data)

        assert 'value' in features.columns
        assert 'day_of_week' in features.columns
        assert 'month' in features.columns
        assert any('lag_' in col for col in features.columns)
        assert any('rolling_mean' in col for col in features.columns)
