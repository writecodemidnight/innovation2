"""
随机森林预测模型

用于预测校园活动的资源需求

随机森林是集成学习方法，通过构建多个决策树并取平均来提高预测准确性和稳定性。
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
import warnings

try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
    from sklearn.metrics import mean_absolute_error, mean_squared_error
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    warnings.warn("scikit-learn not available, using simplified Random Forest implementation")


@dataclass
class RFMetrics:
    """随机森林模型评估指标"""
    mae: float
    rmse: float
    mape: float
    r2: float
    feature_importance: Dict[str, float]


@dataclass
class RFResult:
    """随机森林预测结果"""
    forecast: np.ndarray
    confidence_intervals: Optional[np.ndarray]
    tree_predictions: Optional[np.ndarray]


class FeatureEngineer:
    """特征工程：从时间序列提取特征"""

    @staticmethod
    def extract_features(
        data: pd.Series,
        window_sizes: List[int] = None
    ) -> pd.DataFrame:
        """
        提取时间序列特征

        Args:
            data: 时间序列数据
            window_sizes: 滚动窗口大小

        Returns:
            特征DataFrame
        """
        if window_sizes is None:
            window_sizes = [7, 14, 30]

        features = pd.DataFrame(index=data.index)
        features['value'] = data.values

        # 时间特征
        if isinstance(data.index, pd.DatetimeIndex):
            features['day_of_week'] = data.index.dayofweek
            features['month'] = data.index.month
            features['day_of_month'] = data.index.day
            features['is_weekend'] = (data.index.dayofweek >= 5).astype(int)
            features['quarter'] = data.index.quarter

        # 滞后特征
        for lag in [1, 2, 3, 7]:
            features[f'lag_{lag}'] = data.shift(lag)

        # 滚动统计特征
        for window in window_sizes:
            features[f'rolling_mean_{window}'] = data.rolling(window=window).mean()
            features[f'rolling_std_{window}'] = data.rolling(window=window).std()
            features[f'rolling_max_{window}'] = data.rolling(window=window).max()
            features[f'rolling_min_{window}'] = data.rolling(window=window).min()

        # 趋势特征
        features['trend'] = np.arange(len(data))

        # 增长率特征
        features['growth_rate'] = data.pct_change().fillna(0)

        return features.ffill().fillna(0)


class RandomForestForecaster:
    """
    随机森林时间序列预测器

    使用场景:
    - 多特征时间序列预测
    - 非线性关系建模
    - 特征重要性分析

    示例:
        forecaster = RandomForestForecaster(n_estimators=100, max_depth=10)
        forecaster.fit(train_data, feature_df)
        forecast = forecaster.predict(steps=30)
    """

    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: Optional[int] = None,
        min_samples_split: int = 2,
        min_samples_leaf: int = 1,
        max_features: str = "sqrt",
        random_state: int = 42,
        auto_tune: bool = False,
        prediction_interval: bool = True
    ):
        """
        初始化随机森林预测器

        Args:
            n_estimators: 树的数量
            max_depth: 最大深度
            min_samples_split: 节点分裂最小样本数
            min_samples_leaf: 叶子节点最小样本数
            max_features: 最大特征数
            random_state: 随机种子
            auto_tune: 是否自动调参
            prediction_interval: 是否计算预测区间
        """
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.max_features = max_features
        self.random_state = random_state
        self.auto_tune = auto_tune
        self.prediction_interval = prediction_interval

        self.model = None
        self.feature_engineer = FeatureEngineer()
        self.feature_names = None
        self.fitted = False

    def _build_model(self) -> RandomForestRegressor:
        """构建随机森林模型"""
        if not SKLEARN_AVAILABLE:
            return None

        return RandomForestRegressor(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            min_samples_split=self.min_samples_split,
            min_samples_leaf=self.min_samples_leaf,
            max_features=self.max_features,
            random_state=self.random_state,
            n_jobs=-1
        )

    def fit(
        self,
        data: pd.Series,
        feature_df: Optional[pd.DataFrame] = None,
        validation_split: float = 0.2
    ) -> 'RandomForestForecaster':
        """
        训练随机森林模型

        Args:
            data: 目标时间序列
            feature_df: 外部特征（可选）
            validation_split: 验证集比例

        Returns:
            self
        """
        # 特征工程
        if feature_df is None:
            features = self.feature_engineer.extract_features(data)
        else:
            base_features = self.feature_engineer.extract_features(data)
            features = pd.concat([base_features, feature_df], axis=1)

        self.feature_names = features.columns.tolist()

        # 准备训练数据
        X = features.iloc[:-1]  # 特征不包含最后一个
        y = data.iloc[1:].values  # 目标是下一个值

        # 对齐长度
        min_len = min(len(X), len(y))
        X = X.iloc[:min_len]
        y = y[:min_len]

        if not SKLEARN_AVAILABLE:
            # 简化版：使用均值预测
            self.simplified_model = {'mean': np.mean(y)}
            self.fitted = True
            return self

        # 划分训练集和验证集
        split_idx = int(len(X) * (1 - validation_split))
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]

        # 自动调参
        if self.auto_tune:
            self._auto_tune_hyperparameters(X_train, y_train)
        else:
            self.model = self._build_model()

        # 训练
        self.model.fit(X_train, y_train)
        self.fitted = True

        return self

    def _auto_tune_hyperparameters(
        self,
        X_train: pd.DataFrame,
        y_train: np.ndarray
    ):
        """自动调参"""
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [5, 10, None],
            'min_samples_split': [2, 5],
            'min_samples_leaf': [1, 2]
        }

        base_model = RandomForestRegressor(random_state=self.random_state)

        tscv = TimeSeriesSplit(n_splits=3)

        grid_search = GridSearchCV(
            base_model,
            param_grid,
            cv=tscv,
            scoring='neg_mean_squared_error',
            n_jobs=-1
        )

        grid_search.fit(X_train, y_train)
        self.model = grid_search.best_estimator_

    def predict(
        self,
        steps: int = 30,
        last_features: Optional[pd.DataFrame] = None
    ) -> RFResult:
        """
        预测未来值

        Args:
            steps: 预测步数
            last_features: 最后已知特征

        Returns:
            RFResult对象
        """
        if not self.fitted:
            raise RuntimeError("模型尚未训练，请先调用fit()")

        if not SKLEARN_AVAILABLE:
            return self._predict_simplified(steps)

        if last_features is None:
            raise ValueError("使用sklearn模型时需要提供last_features参数")

        predictions = []
        tree_preds = []

        # 迭代预测
        current_features = last_features.copy()

        for _ in range(steps):
            pred = self.model.predict(current_features.iloc[-1:])[0]

            # 获取每棵树的预测
            if hasattr(self.model, 'estimators_'):
                trees = [tree.predict(current_features.iloc[-1:])[0]
                         for tree in self.model.estimators_]
                tree_preds.append(trees)

            predictions.append(pred)

            # 更新特征（简化版，实际应用中需要更复杂的特征更新）
            current_features = self._update_features(current_features, pred)

        predictions = np.array(predictions)

        # 计算置信区间
        confidence_intervals = None
        if self.prediction_interval and tree_preds:
            tree_preds_array = np.array(tree_preds)
            std_preds = np.std(tree_preds_array, axis=1)
            confidence_intervals = np.array([
                [max(0, pred - 1.96 * std), pred + 1.96 * std]
                for pred, std in zip(predictions, std_preds)
            ])

        return RFResult(
            forecast=predictions,
            confidence_intervals=confidence_intervals,
            tree_predictions=np.array(tree_preds) if tree_preds else None
        )

    def _predict_simplified(self, steps: int) -> RFResult:
        """简化版预测"""
        mean_val = self.simplified_model.get('mean', 0)
        return RFResult(
            forecast=np.array([mean_val] * steps),
            confidence_intervals=None,
            tree_predictions=None
        )

    def _update_features(
        self,
        features: pd.DataFrame,
        new_value: float
    ) -> pd.DataFrame:
        """更新特征用于迭代预测"""
        new_row = features.iloc[-1:].copy()

        # 更新滞后特征
        for col in new_row.columns:
            if col.startswith('lag_'):
                lag = int(col.split('_')[1])
                if lag == 1:
                    new_row[col] = new_value
                else:
                    prev_lag_col = f'lag_{lag-1}'
                    if prev_lag_col in features.columns:
                        new_row[col] = features[prev_lag_col].iloc[-1]

        # 更新滚动统计（简化）
        new_row['value'] = new_value

        return pd.concat([features, new_row], ignore_index=True)

    def evaluate(
        self,
        test_data: pd.Series,
        feature_df: Optional[pd.DataFrame] = None
    ) -> RFMetrics:
        """
        评估模型性能

        Args:
            test_data: 测试数据
            feature_df: 外部特征

        Returns:
            评估指标
        """
        # 准备测试特征
        if feature_df is None:
            test_features = self.feature_engineer.extract_features(test_data)
        else:
            base_features = self.feature_engineer.extract_features(test_data)
            test_features = pd.concat([base_features, feature_df], axis=1)

        X_test = test_features.iloc[:-1]
        y_test = test_data.iloc[1:].values

        min_len = min(len(X_test), len(y_test))
        X_test = X_test.iloc[:min_len]
        y_test = y_test[:min_len]

        if not SKLEARN_AVAILABLE:
            predictions = np.array([self.simplified_model['mean']] * len(y_test))
            return RFMetrics(
                mae=np.mean(np.abs(y_test - predictions)),
                rmse=np.sqrt(np.mean((y_test - predictions) ** 2)),
                mape=np.mean(np.abs((y_test - predictions) / (y_test + 1e-10))) * 100,
                r2=0.0,
                feature_importance={}
            )

        predictions = self.model.predict(X_test)

        # 计算指标
        mae = mean_absolute_error(y_test, predictions)
        rmse = np.sqrt(mean_squared_error(y_test, predictions))
        mape = np.mean(np.abs((y_test - predictions) / (y_test + 1e-10))) * 100
        r2 = self.model.score(X_test, y_test)

        # 特征重要性
        importance = dict(zip(
            self.feature_names,
            self.model.feature_importances_
        ))

        return RFMetrics(
            mae=mae,
            rmse=rmse,
            mape=mape,
            r2=r2,
            feature_importance=importance
        )

    def get_feature_importance(self, top_n: int = 10) -> List[Tuple[str, float]]:
        """
        获取特征重要性排序

        Args:
            top_n: 返回前N个重要特征

        Returns:
            (特征名, 重要性) 列表
        """
        if not SKLEARN_AVAILABLE or self.model is None:
            return []

        importance = list(zip(
            self.feature_names,
            self.model.feature_importances_
        ))
        importance.sort(key=lambda x: x[1], reverse=True)

        return importance[:top_n]

    def explain_prediction(
        self,
        features: pd.DataFrame,
        method: str = "feature_importance"
    ) -> Dict:
        """
        解释预测结果

        Args:
            features: 特征
            method: 解释方法

        Returns:
            解释结果
        """
        if not SKLEARN_AVAILABLE:
            return {"method": "simplified", "explanation": "模型不可用"}

        if method == "feature_importance":
            prediction = self.model.predict(features)[0]

            # 获取特征贡献
            contributions = []
            for i, feature in enumerate(self.feature_names):
                contrib = features.iloc[0, i] * self.model.feature_importances_[i]
                contributions.append((feature, contrib))

            contributions.sort(key=lambda x: abs(x[1]), reverse=True)

            return {
                "prediction": prediction,
                "top_contributing_features": contributions[:5],
                "method": "feature_importance"
            }

        return {"method": method, "explanation": "不支持的方法"}
