from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "auto_affiliate",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.domains.sys_worker.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Ho_Chi_Minh",
    enable_utc=True,
    task_routes={
        "app.domains.sys_worker.tasks.*": {"queue": "main-queue"},
    },
    task_track_started=True,
)
