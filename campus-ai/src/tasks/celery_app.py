# campus-ai/src/tasks/celery_app.py

from celery import Celery
from celery.signals import task_success, task_failure
import os

# Celery配置 - 使用环境变量或默认值
broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

celery_app = Celery(
    'campus_club_ml',
    broker=broker_url,
    backend=result_backend,
    include=[
        'src.tasks.clustering_tasks',
        'src.tasks.scheduling_tasks',
        'src.tasks.forecasting_tasks',
    ]
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1小时
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
