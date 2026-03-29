import logging

from app.core.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.domains.sys_worker.tasks.test_worker_task", bind=True)
def test_worker_task(self, msg: str) -> dict:
    """
    Sample background task — logs message and returns status.
    Used to verify Celery/Redis integration is working.
    """
    logger.info(f"[test_worker_task] Received: {msg}")
    return {"status": "processed", "msg": msg, "task_id": self.request.id}
