"""
Campaign API Router — Extended with automation config + task triggers
=====================================================================

Endpoints:
  GET    /campaigns                           — List all campaigns
  POST   /campaigns                           — Create campaign
  PUT    /campaigns/{id}                      — Update basic info (name, status)
  PUT    /campaigns/{id}/automation           — Update automation config
  POST   /campaigns/{id}/run-comment          — Trigger batch FB comment (async Celery)
  GET    /campaigns/{id}/task/{task_id}       — Get Celery task status
  DELETE /campaigns/{id}                      — Delete campaign
"""

import json
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.core.database import get_session
from app.domains.admin.dependencies import get_current_admin
from app.domains.campaign.models import Campaign

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


# ─── Schemas ──────────────────────────────────────────────────────────────────


class CampaignCreate(BaseModel):
    name: str
    status: str = "draft"


class CampaignBasicUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None


class CampaignAutomationConfig(BaseModel):
    shopee_keyword: Optional[str] = None
    affiliate_link: Optional[str] = None
    comment_template: Optional[str] = None
    facebook_post_urls: Optional[List[str]] = None  # list từ frontend; serialize thành JSON string
    target_device_udid: Optional[str] = None
    comment_delay_seconds: Optional[float] = None


class RunCommentRequest(BaseModel):
    """Override params — nếu không truyền thì dùng config từ campaign."""
    post_urls: Optional[List[str]] = None
    comment_text: Optional[str] = None
    udid: Optional[str] = None
    delay_between: Optional[float] = None


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[dict] = None
    error: Optional[str] = None


# ─── Endpoints ────────────────────────────────────────────────────────────────


@router.get("", response_model=List[Campaign])
def list_campaigns(
    session: Session = Depends(get_session),
    _admin=Depends(get_current_admin),
):
    return session.exec(select(Campaign)).all()


@router.post("", response_model=Campaign)
def create_campaign(
    payload: CampaignCreate,
    session: Session = Depends(get_session),
    _admin=Depends(get_current_admin),
):
    campaign = Campaign(name=payload.name, status=payload.status)
    session.add(campaign)
    session.commit()
    session.refresh(campaign)
    return campaign


@router.put("/{campaign_id}", response_model=Campaign)
def update_campaign(
    campaign_id: str,
    payload: CampaignCreate,
    session: Session = Depends(get_session),
    _admin=Depends(get_current_admin),
):
    """Cập nhật thông tin cơ bản (name, status)."""
    campaign = session.get(Campaign, uuid.UUID(campaign_id))
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    campaign.name = payload.name
    campaign.status = payload.status
    campaign.updated_at = datetime.utcnow()
    session.add(campaign)
    session.commit()
    session.refresh(campaign)
    return campaign


@router.put("/{campaign_id}/automation", response_model=Campaign)
def update_campaign_automation(
    campaign_id: str,
    payload: CampaignAutomationConfig,
    session: Session = Depends(get_session),
    _admin=Depends(get_current_admin),
):
    """
    Cập nhật cấu hình automation cho campaign:
    keyword Shopee, affiliate link, template comment, danh sách post FB, thiết bị.
    """
    campaign = session.get(Campaign, uuid.UUID(campaign_id))
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if payload.shopee_keyword is not None:
        campaign.shopee_keyword = payload.shopee_keyword
    if payload.affiliate_link is not None:
        campaign.affiliate_link = payload.affiliate_link
    if payload.comment_template is not None:
        campaign.comment_template = payload.comment_template
    if payload.facebook_post_urls is not None:
        # serialize list → JSON string để lưu vào TEXT column
        campaign.facebook_post_urls = json.dumps(payload.facebook_post_urls, ensure_ascii=False)
    if payload.target_device_udid is not None:
        campaign.target_device_udid = payload.target_device_udid
    if payload.comment_delay_seconds is not None:
        campaign.comment_delay_seconds = payload.comment_delay_seconds

    campaign.updated_at = datetime.utcnow()
    session.add(campaign)
    session.commit()
    session.refresh(campaign)
    return campaign


@router.post("/{campaign_id}/run-comment")
def run_campaign_comment(
    campaign_id: str,
    body: RunCommentRequest = RunCommentRequest(),
    session: Session = Depends(get_session),
    _admin=Depends(get_current_admin),
):
    """
    Trigger batch Facebook comment seeding cho campaign.
    Enqueue Celery task trên queue appium_phone.

    UDID resolution priority:
      1. body.udid (override tức thì)
      2. campaign.target_device_udid (đã cấu hình trong tab Automation)
      3. Thiết bị đầu tiên có status=online trong bảng Device
    """
    from app.domains.sys_worker.seeding_tasks import exec_fb_batch_comment
    from app.domains.devices.models import Device

    campaign = session.get(Campaign, uuid.UUID(campaign_id))
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Resolve post URLs
    post_urls = body.post_urls
    if not post_urls:
        if campaign.facebook_post_urls:
            try:
                post_urls = json.loads(campaign.facebook_post_urls)
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=422,
                    detail="facebook_post_urls trong campaign không phải JSON hợp lệ",
                )
        else:
            raise HTTPException(
                status_code=412,
                detail="Chưa cấu hình facebook_post_urls cho campaign. Điền vào tab Automation trước.",
            )

    # Resolve comment text
    comment_text = body.comment_text
    if not comment_text:
        if campaign.comment_template and campaign.affiliate_link:
            comment_text = campaign.comment_template.replace(
                "{affiliate_link}", campaign.affiliate_link
            )
        elif campaign.affiliate_link:
            comment_text = campaign.affiliate_link
        else:
            raise HTTPException(
                status_code=412,
                detail="Chưa cấu hình comment_template hoặc affiliate_link cho campaign.",
            )

    # Resolve device UDID
    # Priority: body override > campaign config > first online device in DB
    udid = body.udid or campaign.target_device_udid
    if not udid:
        # Fallback: lấy thiết bị đầu tiên đang online từ bảng Device
        online_device = session.exec(
            select(Device).where(Device.status == "online")
        ).first()
        if online_device:
            udid = online_device.udid

    if not udid:
        raise HTTPException(
            status_code=412,
            detail=(
                "Chưa có thiết bị khả dụng. "
                "Vào trang Thiết Bị → thêm thiết bị và bật trạng thái Online, "
                "hoặc chọn thiết bị trong tab Automation của campaign."
            ),
        )

    # Resolve delay
    delay = body.delay_between or campaign.comment_delay_seconds or 30.0

    try:
        task = exec_fb_batch_comment.delay(
            udid=udid,
            post_urls=post_urls,
            comment_text=comment_text,
            delay_between=delay,
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Không thể enqueue task: {e}")

    return {
        "task_id": task.id,
        "status": "queued",
        "campaign_id": str(campaign.id),
        "campaign_name": campaign.name,
        "post_count": len(post_urls),
        "udid": udid,
        "message": f"Đã enqueue {len(post_urls)} post để comment. Task ID: {task.id}",
    }


@router.get("/{campaign_id}/task/{task_id}", response_model=TaskStatusResponse)
def get_task_status(
    campaign_id: str,
    task_id: str,
    _admin=Depends(get_current_admin),
):
    """Kiểm tra trạng thái Celery task theo task_id."""
    from celery.result import AsyncResult
    from app.core.celery_app import celery_app

    result = AsyncResult(task_id, app=celery_app)

    response = TaskStatusResponse(task_id=task_id, status=result.state)

    if result.state == "SUCCESS":
        response.result = result.result
    elif result.state == "FAILURE":
        response.error = str(result.result)

    return response


@router.delete("/{campaign_id}")
def delete_campaign(
    campaign_id: str,
    session: Session = Depends(get_session),
    _admin=Depends(get_current_admin),
):
    campaign = session.get(Campaign, uuid.UUID(campaign_id))
    if campaign:
        session.delete(campaign)
        session.commit()
    return {"message": "Deleted"}
