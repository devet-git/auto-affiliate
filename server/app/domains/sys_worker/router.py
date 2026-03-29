from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.domains.admin.dependencies import get_current_admin
from app.domains.sys_worker.tasks import test_worker_task

router = APIRouter(prefix="/worker", tags=["worker"])


class TestJobRequest(BaseModel):
    msg: str


class TestJobResponse(BaseModel):
    task_id: str
    status: str


@router.post("/test", response_model=TestJobResponse)
async def trigger_test_job(
    body: TestJobRequest,
    _admin: dict = Depends(get_current_admin),
) -> TestJobResponse:
    """
    Trigger a test background job to verify Celery/Redis integration.
    Requires valid admin JWT token.
    """
    try:
        task = test_worker_task.delay(body.msg)
        return TestJobResponse(task_id=str(task.id), status="queued")
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Queue unavailable — is Redis running? ({type(e).__name__})",
        )

from sqlmodel import Session, select
from typing import Optional
from app.core.database import get_session
from app.domains.sys_worker.models import TaskLog, AppSetting

@router.get("/logs")
def get_logs(
    status: Optional[str] = None,
    task_name: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    session: Session = Depends(get_session),
    _admin: dict = Depends(get_current_admin),
):
    query = select(TaskLog).order_by(TaskLog.id.desc())
    if status:
        query = query.where(TaskLog.status == status)
    if task_name:
        query = query.where(TaskLog.task_name == task_name)
    
    logs = session.exec(query.offset(offset).limit(limit)).all()
    total = session.exec(select(TaskLog)).all() # basic count for frontend pagination
    return {"data": logs, "total": len(total)}

class AppSettingRequest(BaseModel):
    key: str
    value: str

@router.get("/settings/{key}")
def get_setting(
    key: str,
    session: Session = Depends(get_session),
    _admin: dict = Depends(get_current_admin)
):
    setting = session.get(AppSetting, key)
    if not setting:
        return {"key": key, "value": "7"} # Default log retention
    return setting

@router.post("/settings")
def update_setting(
    body: AppSettingRequest,
    session: Session = Depends(get_session),
    _admin: dict = Depends(get_current_admin)
):
    setting = session.get(AppSetting, body.key)
    if not setting:
        setting = AppSetting(key=body.key, value=body.value)
    else:
        setting.value = body.value
        
    session.add(setting)
    session.commit()
    session.refresh(setting)
    return setting
