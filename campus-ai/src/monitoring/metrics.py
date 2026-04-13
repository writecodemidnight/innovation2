# campus-ai/src/monitoring/metrics.py

import time
from functools import wraps
from typing import Optional

# Try to import prometheus_client, but provide stubs if not available
try:
    from prometheus_client import Counter, Histogram, Gauge, Info
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

    # Stub classes for when prometheus_client is not installed
    class _MetricStub:
        def __init__(self, *args, **kwargs):
            pass
        def labels(self, *args, **kwargs):
            return self
        def observe(self, *args, **kwargs):
            pass
        def inc(self, *args, **kwargs):
            pass
        def set(self, *args, **kwargs):
            pass

    class Counter(_MetricStub):
        pass

    class Histogram(_MetricStub):
        pass

    class Gauge(_MetricStub):
        pass

    class Info(_MetricStub):
        pass


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


def update_cache_hit_rate(model_type: str, hit_rate: float):
    """更新缓存命中率指标"""
    CACHE_HIT_RATE.labels(model_type=model_type).set(hit_rate)


def update_active_models(model_type: str, count: int):
    """更新活跃模型数量指标"""
    ACTIVE_MODELS.labels(model_type=model_type).set(count)


def record_drift_detected(model_type: str, feature_name: str, detected: bool):
    """记录漂移检测状态"""
    DRIFT_DETECTED.labels(
        model_type=model_type,
        feature_name=feature_name
    ).set(1 if detected else 0)
