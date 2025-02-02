import json
import os
import logging
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from database.database import get_db, Country, CountryData
from models.models import Campaign as CampaignModel
from schemas.schema import Campaign as CampaignSchema, CampaignCreate, Payout as PayoutSchema, PayoutCreate, PayoutUpdate
from service.service import campaign_service, payout_service
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class CampaignBase(BaseModel):
    country: Country  # Required
    
class PayoutBase(BaseModel):
    country: Country  # Required

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])

@router.post("/", response_model=CampaignSchema)
def create_campaign(campaign: CampaignCreate, db: Session = Depends(get_db)):
    """
    Create a new campaign with payouts
    
    Example request body:
    ```json
    {
        "title": "Campaign Title",
        "landing_url": "https://example.com",
        "is_running": false,
        "country": "US",
        "payouts": [
            {
                "country": "US",
                "amount": 100.00
            }
        ]
    }
    ```
    """
    try:
        if not isinstance(campaign.country, Country):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid country: {campaign.country}"
            )
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
    is_running: Optional[bool] = None,
    country: Optional[Country] = None
):
    filters = {
        "title": title, 
        "landing_url": landing_url, 
        "is_running": is_running,
        "country": country
    }
    return campaign_service.get_campaigns(db, skip, limit, filters)

@router.delete("/{campaign_id}")
def delete_campaign(campaign_id: int, db: Session = Depends(get_db)):
    try:
        success = campaign_service.delete_campaign(db, campaign_id)
        if not success:
            raise HTTPException(status_code=404, detail="Campaign not found")
        return {"message": "Campaign deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{campaign_id}/toggle", response_model=CampaignSchema)
def toggle_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """Toggle campaign active status"""
    try:
        return campaign_service.toggle_campaign(db, campaign_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/countries", response_model=List[Country])
def get_available_countries():
    """Get list of available country codes"""
    # Get all country members from enum
    countries = list(Country.__members__.values())
    logger.info(f"Returning {len(countries)} countries")
    return countries

@router.get("/{campaign_id}/payouts", response_model=List[PayoutSchema])
def get_campaign_payouts(campaign_id: int, db: Session = Depends(get_db)):
    return payout_service.get_campaign_payouts(db, campaign_id)

@router.get("/{campaign_id}/payouts/country/{country}", response_model=PayoutSchema)
def get_country_payout(
    campaign_id: int, 
    country: Country,
    db: Session = Depends(get_db)
):
    try:
        payout = payout_service.get_country_payout(db, campaign_id, country)
        if not payout:
            raise HTTPException(status_code=404, detail="Payout not found for country")
        return payout
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{campaign_id}/payouts", response_model=PayoutSchema)
def add_campaign_payout(
    campaign_id: int,
    payout: PayoutCreate = Body(
        ...,
        example={
            "country": "US",
            "amount": 100.00
        }
    ),
    db: Session = Depends(get_db)
):
    """
    Add a new payout to a campaign
    """
    return payout_service.create_payout(db, campaign_id, payout)

@router.put("/payouts/{payout_id}", response_model=PayoutSchema)
def update_payout(
    payout_id: int, 
    payout: PayoutUpdate, 
    db: Session = Depends(get_db)
):
    try:
        updated_payout = payout_service.update_payout(db, payout_id, payout)
        if not updated_payout:
            raise HTTPException(status_code=404, detail="Payout not found")
        return updated_payout
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/payouts/{payout_id}")
def delete_payout(payout_id: int, db: Session = Depends(get_db)):
    try:
        success = payout_service.delete_payout(db, payout_id)
        if not success:
            raise HTTPException(status_code=404, detail="Payout not found")
        return {"message": "Payout deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

def load_countries():
    try:
        filepath = os.path.join(os.path.dirname(__file__), 'countries.json')
        logger.info(f"Loading countries from: {filepath}")
        
        with open(filepath) as f:
            data = json.load(f)
            # Filter valid countries
            countries = [
                country for country in data['countries']
                if country['COUNTRY_CODE'] and country['COUNTRY_CODE'] != "-"
            ]
            
            logger.info(f"Loaded {len(countries)} valid countries")
            return countries
    except Exception as e:
        logger.error(f"Failed to load countries: {e}")
        raise