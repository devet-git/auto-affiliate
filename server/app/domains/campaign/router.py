from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from pydantic import BaseModel
from app.core.database import get_session
from app.domains.campaign.models import Campaign
from app.domains.admin.dependencies import get_current_admin

router = APIRouter(prefix="/campaigns", tags=["campaigns"])

class CampaignCreate(BaseModel):
    name: str
    status: str

@router.get("", response_model=List[Campaign])
def list_campaigns(session: Session = Depends(get_session), admin=Depends(get_current_admin)):
    return session.exec(select(Campaign)).all()

@router.post("", response_model=Campaign)
def create_campaign(payload: CampaignCreate, session: Session = Depends(get_session), admin=Depends(get_current_admin)):
    campaign = Campaign(name=payload.name, status=payload.status)
    session.add(campaign)
    session.commit()
    session.refresh(campaign)
    return campaign

@router.delete("/{campaign_id}")
def delete_campaign(campaign_id: str, session: Session = Depends(get_session), admin=Depends(get_current_admin)):
    campaign = session.get(Campaign, campaign_id)
    if campaign:
        session.delete(campaign)
        session.commit()
    return {"message": "Deleted"}
