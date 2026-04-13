"""
ARIMA时间序列预测模型

用于预测校园活动的资源需求（场地、预算、人力等）

ARIMA(p,d,q)模型:
- p: 自回归阶数
- d: 差分阶数
- q: 移动平均阶数
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import warnings

# 使用statsmodels实现ARIMA
try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.stattools import adfuller, acf, pacf
    from statsmodels.stats.diagnostic import acorr_ljungbox
    from statsmodels.tsa.seasonal import seasonal_decompose
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    warnings.warn("statsmodels not available, using simplified ARIMA implementation")


@dataclass
class ARIMAResult:
    """ARIMA预测结果"""
    forecast: np.ndarray
    confidence_intervals: Optional[np.ndarray]
    model_params: Dict[str, any]
    aic: float
    bic: float
    residuals: Optional[np.ndarray]


@dataclass
class ARIMAMetrics:
    """ARIMA模型评估指标"""
    mae: float  # 平均绝对误差
    rmse: float  # 均方根误差
    mape: float  # 平均绝对百分比误差
    aic: float  # 赤池信息准则
    bic: float  # 贝叶斯信息准则


class ARIMAForecaster:
    """
    ARIMA时间序列预测器

    使用场景:
    - 预测活动参与人数
    - 预测场地使用率
    - 预测预算需求
    - 预测物资消耗

    示例:
        forecaster = ARIMAForecaster(order=(2,1,2), seasonal_order=(1,1,1,12))
        forecaster.fit(train_data)
        forecast = forecaster.predict(steps=30)
    """

    def __init__(
        self,
        order: Tuple[int, int, int] = (1, 1, 1),
        seasonal_order: Optional[Tuple[int, int, int, int]] = None,
        auto_select: bool = True,
        max_p: int = 5,
        max_d: int = 2,
        max_q: int = 5
    ):
        """
        初始化ARIMA预测器

        Args:
            order: ARIMA阶数 (p,d,q)
            seasonal_order: 季节性ARIMA阶数 (P,D,Q,s)
            auto_select: 是否自动选择最优参数
            max_p, max_d, max_q: 自动选择时的参数范围
        """
        self.order = order
        self.seasonal_order = seasonal_order
        self.auto_select = auto_select
        self.max_p = max_p
        self.max_d = max_d
        self.max_q = max_q

        self.model = None
        self.fitted_model = None
        self.data: Optional[pd.Series] = None
        self.fitted = False

    def _check_stationarity(self, series: pd.Series) -> Tuple[bool, float]:
        """
        ADF检验检查序列平稳性

        Returns:
            (是否平稳, p值)
        """
        if not STATSMODELS_AVAILABLE:
            # 简化版：通过方差变化判断
            half = len(series) // 2
            var1 = series[:half].var()
            var2 = series[half:].var()
            return abs(var1 - var2) / (var1 + 1e-10) < 0.5, 0.1

        result = adfuller(series.dropna())
        is_stationary = result[1] <= 0.05
        return is_stationary, result[1]

    def _determine_d(self, series: pd.Series, max_d: int = 2) -> int:
        """确定差分阶数d"""
        for d in range(max_d + 1):
            if d == 0:
                test_series = series
            else:
                test_series = series.diff(d).dropna()

            is_stationary, _ = self._check_stationarity(test_series)
            if is_stationary:
                return d

        return max_d

    def _auto_select_order(self, series: pd.Series) -> Tuple[int, int, int]:
        """
        自动选择最优ARIMA参数

        使用AIC准则选择最优(p,d,q)组合
        """
        d = self._determine_d(series, self.max_d)

        if not STATSMODELS_AVAILABLE:
            # 简化版：使用默认参数
            return (1, d, 1)

        best_aic = float('inf')
        best_order = (1, d, 1)

        # 网格搜索
        for p in range(self.max_p + 1):
            for q in range(self.max_q + 1):
                if p == 0 and q == 0:
                    continue

                try:
                    model = ARIMA(series, order=(p, d, q))
                    fitted = model.fit()

                    if fitted.aic < best_aic:
                        best_aic = fitted.aic
                        best_order = (p, d, q)

                except Exception:
                    continue

        return best_order

    def fit(self, data: pd.Series) -> 'ARIMAForecaster':
        """
        训练ARIMA模型

        Args:
            data: 时间序列数据，index应为DatetimeIndex

        Returns:
            self
        """
        self.data = data.copy()

        # 自动选择参数
        if self.auto_select:
            self.order = self._auto_select_order(self.data)

        if not STATSMODELS_AVAILABLE:
            # 简化版实现：使用移动平均+趋势
            self.fitted = True
            return self

        # 构建并拟合模型
        try:
            if self.seasonal_order:
                self.model = ARIMA(
                    self.data,
                    order=self.order,
                    seasonal_order=self.seasonal_order
                )
            else:
                self.model = ARIMA(self.data, order=self.order)

            self.fitted_model = self.model.fit()
            self.fitted = True

        except Exception as e:
            raise RuntimeError(f"ARIMA模型拟合失败: {e}")

        return self

    def predict(
        self,
        steps: int = 30,
        alpha: float = 0.05
    ) -> ARIMAResult:
        """
        预测未来值

        Args:
            steps: 预测步数
            alpha: 置信区间显著性水平

        Returns:
            ARIMAResult对象
        """
        if not self.fitted:
            raise RuntimeError("模型尚未训练，请先调用fit()")

        if not STATSMODELS_AVAILABLE:
            # 简化版预测
            return self._simplified_predict(steps)

        # 获取预测结果
        forecast_result = self.fitted_model.get_forecast(steps=steps)
        forecast_mean = forecast_result.predicted_mean.values

        # 置信区间
        conf_int = forecast_result.conf_int(alpha=alpha).values

        return ARIMAResult(
            forecast=forecast_mean,
            confidence_intervals=conf_int,
            model_params={
                'order': self.order,
                'seasonal_order': self.seasonal_order,
                'params': self.fitted_model.params.to_dict() if hasattr(self.fitted_model, 'params') else {}
            },
            aic=self.fitted_model.aic,
            bic=self.fitted_model.bic,
            residuals=self.fitted_model.resid.values if hasattr(self.fitted_model, 'resid') else None
        )

    def _simplified_predict(self, steps: int) -> ARIMAResult:
        """简化版预测（当statsmodels不可用时）"""
        # 使用指数平滑
        values = self.data.values
        alpha = 0.3  # 平滑系数

        # 计算平滑值
        smoothed = [values[0]]
        for i in range(1, len(values)):
            smoothed.append(alpha * values[i] + (1 - alpha) * smoothed[-1])

        # 预测未来值
        forecast = []
        last_value = smoothed[-1]
        trend = np.mean(np.diff(values[-10:])) if len(values) >= 10 else 0

        for i in range(steps):
            forecast.append(last_value + trend * (i + 1))

        forecast = np.array(forecast)

        return ARIMAResult(
            forecast=forecast,
            confidence_intervals=None,
            model_params={'method': 'simplified_exponential_smoothing'},
            aic=0.0,
            bic=0.0,
            residuals=None
        )

    def evaluate(self, test_data: pd.Series) -> ARIMAMetrics:
        """
        评估模型性能

        Args:
            test_data: 测试数据

        Returns:
            评估指标
        """
        steps = len(test_data)
        forecast_result = self.predict(steps=steps)
        forecast = forecast_result.forecast

        actual = test_data.values

        # 计算指标
        mae = np.mean(np.abs(actual - forecast))
        rmse = np.sqrt(np.mean((actual - forecast) ** 2))
        mape = np.mean(np.abs((actual - forecast) / (actual + 1e-10))) * 100

        return ARIMAMetrics(
            mae=mae,
            rmse=rmse,
            mape=mape,
            aic=forecast_result.aic,
            bic=forecast_result.bic
        )

    def cross_validate(
        self,
        n_splits: int = 5
    ) -> Dict[str, float]:
        """
        时间序列交叉验证

        Args:
            n_splits: 折数

        Returns:
            交叉验证结果
        """
        if self.data is None:
            raise RuntimeError("模型尚未训练")

        n = len(self.data)
        split_size = n // (n_splits + 1)

        mae_scores = []
        rmse_scores = []
        mape_scores = []

        for i in range(n_splits):
            train_end = split_size * (i + 1)
            test_end = train_end + split_size

            train_data = self.data[:train_end]
            test_data = self.data[train_end:test_end]

            if len(test_data) == 0:
                break

            # 临时训练模型
            temp_forecaster = ARIMAForecaster(order=self.order)
            temp_forecaster.fit(train_data)

            metrics = temp_forecaster.evaluate(test_data)
            mae_scores.append(metrics.mae)
            rmse_scores.append(metrics.rmse)
            mape_scores.append(metrics.mape)

        return {
            'mae_mean': np.mean(mae_scores),
            'mae_std': np.std(mae_scores),
            'rmse_mean': np.mean(rmse_scores),
            'rmse_std': np.std(rmse_scores),
            'mape_mean': np.mean(mape_scores),
            'mape_std': np.std(mape_scores)
        }

    def get_diagnostics(self) -> Dict:
        """获取模型诊断信息"""
        if not self.fitted or not STATSMODELS_AVAILABLE:
            return {}

        residuals = self.fitted_model.resid

        # Ljung-Box检验残差白噪声
        try:
            lb_test = acorr_ljungbox(residuals, lags=10, return_df=True)
            lb_pvalues = lb_test['lb_pvalue'].values
        except:
            lb_pvalues = []

        return {
            'residual_mean': float(np.mean(residuals)),
            'residual_std': float(np.std(residuals)),
            'ljung_box_pvalues': lb_pvalues.tolist() if len(lb_pvalues) > 0 else [],
            'is_residual_white_noise': all(p > 0.05 for p in lb_pvalues) if len(lb_pvalues) > 0 else None
        }

    def forecast_resource_needs(
        self,
        planning_horizon_days: int = 30,
        resource_type: str = "participants"
    ) -> Dict:
        """
        预测资源需求（业务接口）

        Args:
            planning_horizon_days: 规划时间范围（天）
            resource_type: 资源类型

        Returns:
            资源需求预测结果
        """
        result = self.predict(steps=planning_horizon_days)

        forecast = result.forecast

        # 计算统计信息
        total_need = np.sum(forecast)
        avg_daily = np.mean(forecast)
        max_daily = np.max(forecast)
        min_daily = np.max([np.min(forecast), 0])

        # 生成日期索引
        if self.data is not None:
            last_date = self.data.index[-1]
            if isinstance(last_date, pd.Timestamp):
                future_dates = pd.date_range(
                    start=last_date + timedelta(days=1),
                    periods=planning_horizon_days,
                    freq='D'
                )
            else:
                future_dates = list(range(len(self.data), len(self.data) + planning_horizon_days))
        else:
            future_dates = list(range(planning_horizon_days))

        return {
            'resource_type': resource_type,
            'planning_horizon_days': planning_horizon_days,
            'forecast': {
                'dates': [str(d) for d in future_dates],
                'values': forecast.tolist()
            },
            'statistics': {
                'total_predicted': round(float(total_need), 2),
                'daily_average': round(float(avg_daily), 2),
                'daily_max': round(float(max_daily), 2),
                'daily_min': round(float(min_daily), 2)
            },
            'model_info': {
                'order': self.order,
                'aic': round(result.aic, 2),
                'bic': round(result.bic, 2)
            }
        }
