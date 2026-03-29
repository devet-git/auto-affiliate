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

from datetime import datetime, timedelta
from sqlmodel import Session, select
from app.core.database import engine
from app.domains.sys_worker.models import TaskLog, AppSetting

@celery_app.task(name="app.domains.sys_worker.tasks.cleanup_expired_logs", bind=True)
def cleanup_expired_logs(self):
    """
    Deletes TaskLogs older than log_retention_days setting.
    """
    with Session(engine) as session:
        setting = session.get(AppSetting, "log_retention_days")
        days = int(setting.value) if setting else 7
        
        threshold = datetime.utcnow() - timedelta(days=days)
        statement = select(TaskLog).where(TaskLog.started_at < threshold)
        expired_logs = session.exec(statement).all()
        
        for log in expired_logs:
            session.delete(log)
        
        session.commit()
        logger.info(f"Cleaned up {len(expired_logs)} expired TaskLogs.")
