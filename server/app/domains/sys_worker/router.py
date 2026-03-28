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
    task = test_worker_task.delay(body.msg)
    return TestJobResponse(task_id=str(task.id), status="queued")
