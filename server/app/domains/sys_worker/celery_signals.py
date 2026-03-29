import json
import traceback
from datetime import datetime
from celery.signals import task_prerun, task_success, task_failure
from sqlmodel import Session, select
from app.core.database import engine
from app.domains.sys_worker.models import TaskLog

@task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **other):
    kw = kwargs or {}
    try:
        with Session(engine) as session:
            log = TaskLog(
                task_id=task_id,
                task_name=task.name if task else "unknown",
                status="STARTED",
                kwargs=kw,
                started_at=datetime.utcnow()
            )
            session.add(log)
            session.commit()
    except Exception as e:
        print(f"Error logging task start: {e}")

@task_success.connect
def task_success_handler(sender=None, result=None, **kwargs):
    task_id = sender.request.id if sender and sender.request else kwargs.get("task_id")
    try:
        with Session(engine) as session:
            statement = select(TaskLog).where(TaskLog.task_id == task_id)
            log = session.exec(statement).first()
            if log:
                log.status = "SUCCESS"
                log.finished_at = datetime.utcnow()
                # Store result safely
                if isinstance(result, (dict, list, str, int, float, bool, type(None))):
                    log.result = {"data": result} if not isinstance(result, dict) else result
                else:
                    log.result = {"data": str(result)}
                session.add(log)
                session.commit()
    except Exception as e:
        print(f"Error logging task success: {e}")

@task_failure.connect
def task_failure_handler(sender=None, exception=None, traceback=None, **kwargs):
    task_id = sender.request.id if getattr(sender, 'request', None) else kwargs.get("task_id")
    try:
        with Session(engine) as session:
            statement = select(TaskLog).where(TaskLog.task_id == task_id)
            log = session.exec(statement).first()
            if log:
                log.status = "FAILED"
                log.finished_at = datetime.utcnow()
                log.error_traceback = str(traceback) if traceback else str(exception)
                session.add(log)
                session.commit()
    except Exception as e:
        print(f"Error logging task failure: {e}")
