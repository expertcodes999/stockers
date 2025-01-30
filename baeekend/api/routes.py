from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database.database import get_db, COUNTRIES_DATA, CountryData
from ..models.models import Campaign as CampaignModel
from ..schemas.schema import Campaign as CampaignSchema, CampaignCreate
from ..service.service import campaign_service

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])

@router.post("/", response_model=CampaignSchema)
def create_campaign(campaign: CampaignCreate, db: Session = Depends(get_db)):
    try:
        return campaign_service.create_campaign(db, campaign)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[CampaignSchema])
def list_campaigns(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    title: Optional[str] = None,
    landing_url: Optional[str] = None,
    is_running: Optional[bool] = None
):
    filters = {"title": title, "landing_url": landing_url, "is_running": is_running}
    return campaign_service.get_campaigns(db, skip, limit, filters)

@router.patch("/{campaign_id}/toggle", response_model=CampaignSchema)
def toggle_campaign(campaign_id: int, db: Session = Depends(get_db)):
    return campaign_service.toggle_campaign(db, campaign_id)


@router.get("/countries", response_model=List[CountryData])
def get_available_countries():
    return [CountryData(**country) for country in COUNTRIES_DATA]

@router.get("/countries/{country_code}/currency")
def get_country_currency(country_code: str):
    country = next(
        (c for c in COUNTRIES_DATA if c["COUNTRY_CODE"] == country_code),
        None
    )
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    return {
        "currency_code": country["CURRENCY_CODE"],
        "currency_name": country["NAME_OF_CURRENCY"]
    }