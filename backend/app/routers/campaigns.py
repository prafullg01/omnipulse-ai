"""Campaigns Router — CRUD, NL generation, simulation."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.database.connection import get_db
from app.models.models import Campaign, CampaignResponse

router = APIRouter()


class CampaignCreate(BaseModel):
    campaign_name: str
    description: Optional[str] = None
    audience: Optional[dict] = None
    channel: Optional[str] = "email"
    offer: Optional[str] = None
    discount_pct: Optional[float] = 0
    variant: Optional[str] = None


@router.post("")
def create_campaign(data: CampaignCreate, db: Session = Depends(get_db)):
    campaign = Campaign(
        campaign_name=data.campaign_name,
        description=data.description,
        audience=data.audience or {},
        channel=data.channel,
        offer=data.offer,
        discount_pct=data.discount_pct,
        variant=data.variant,
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return {"campaign_id": campaign.campaign_id, "campaign_name": campaign.campaign_name, "status": campaign.status}


@router.get("")
def list_campaigns(db: Session = Depends(get_db)):
    campaigns = db.query(Campaign).order_by(desc(Campaign.created_at)).limit(50).all()
    return [
        {
            "campaign_id": c.campaign_id,
            "campaign_name": c.campaign_name,
            "channel": c.channel,
            "offer": c.offer,
            "status": c.status,
            "variant": c.variant,
            "created_at": c.created_at.isoformat(),
        }
        for c in campaigns
    ]


@router.post("/{campaign_id}/launch")
def launch_campaign(campaign_id: str, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).filter(Campaign.campaign_id == campaign_id).first()
    if campaign:
        campaign.status = "active"
        campaign.started_at = datetime.utcnow()
        db.commit()
        return {"status": "launched"}
    return {"error": "Campaign not found"}


@router.get("/{campaign_id}/metrics")
def campaign_metrics(campaign_id: str, db: Session = Depends(get_db)):
    total = db.query(CampaignResponse).filter(CampaignResponse.campaign_id == campaign_id).count()
    opened = db.query(CampaignResponse).filter(CampaignResponse.campaign_id == campaign_id, CampaignResponse.opened == True).count()
    clicked = db.query(CampaignResponse).filter(CampaignResponse.campaign_id == campaign_id, CampaignResponse.clicked == True).count()
    converted = db.query(CampaignResponse).filter(CampaignResponse.campaign_id == campaign_id, CampaignResponse.converted == True).count()
    revenue = db.query(func.sum(CampaignResponse.revenue)).filter(CampaignResponse.campaign_id == campaign_id).scalar() or 0
    
    return {
        "total_sent": total,
        "opened": opened,
        "clicked": clicked,
        "converted": converted,
        "open_rate": round((opened / max(total, 1)) * 100, 1),
        "click_rate": round((clicked / max(total, 1)) * 100, 1),
        "conversion_rate": round((converted / max(total, 1)) * 100, 1),
        "revenue": round(revenue, 2),
    }
