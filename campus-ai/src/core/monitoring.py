from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Histogram, Gauge, REGISTRY
import time
from loguru import logger

# Prometheus指标定义
class Metrics:
    """监控指标收集器"""

    def __init__(self):
        # API请求指标 - 先检查是否已存在，避免重复注册
        self.request_count = self._get_or_create_counter(
            'algorithm_service_requests_total',
            'Total number of API requests',
            ['method', 'endpoint', 'status']
        )

        self.request_duration = self._get_or_create_histogram(
            'algorithm_service_request_duration_seconds',
            'API request duration in seconds',
            ['method', 'endpoint'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
        )

        # 系统资源指标
        self.loaded_models = self._get_or_create_gauge(
            'algorithm_service_models_loaded',
            'Number of models currently loaded in memory'
        )

        self.error_count = self._get_or_create_counter(
            'algorithm_service_errors_total',
            'Total number of errors',
            ['error_type', 'algorithm']
        )

    def _get_or_create_counter(self, name, description, labels):
        """获取或创建Counter指标"""
        try:
            return Counter(name, description, labels)
        except ValueError:
            # 指标已存在，从注册表中获取
            return REGISTRY._names_to_collectors.get(name)

    def _get_or_create_histogram(self, name, description, labels, buckets=None):
        """获取或创建Histogram指标"""
        try:
            if buckets:
                return Histogram(name, description, labels, buckets=buckets)
            return Histogram(name, description, labels)
        except ValueError:
            return REGISTRY._names_to_collectors.get(name)

    def _get_or_create_gauge(self, name, description):
        """获取或创建Gauge指标"""
        try:
            return Gauge(name, description)
        except ValueError:
            return REGISTRY._names_to_collectors.get(name)

    def record_request(self, method: str, endpoint: str, status: str, duration: float):
        """记录API请求指标"""
        if self.request_count:
            self.request_count.labels(method=method, endpoint=endpoint, status=status).inc()
        if self.request_duration:
            self.request_duration.labels(method=method, endpoint=endpoint).observe(duration)

def setup_monitoring(app):
    """设置应用监控"""
    # 1. 基础指标收集
    instrumentator = Instrumentator(
        should_group_status_codes=False,
        excluded_handlers=["/metrics", "/health", "/docs", "/redoc"]
    )
    instrumentator.instrument(app).expose(app)

    # 2. 自定义指标实例
    metrics = Metrics()
    app.state.metrics = metrics

    logger.info("✅ 监控系统初始化完成")
    return metrics