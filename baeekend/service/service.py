from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from ..models.models import Campaign, Payout
from ..schemas.schema import CampaignCreate, Campaign as CampaignSchema
from ..database.database import get_country_details, Country

class CampaignService:
   
    def create_campaign(self, db: Session, campaign: CampaignCreate) -> CampaignSchema:
        # Validate campaign data
        if not campaign.title or not campaign.landing_url:
            raise ValueError("Title and Landing URL are required")
        if not campaign.payouts:
            raise ValueError("At least one payout is required")
            
        # Create campaign
        db_campaign = Campaign(
            title=campaign.title,
            landing_url=campaign.landing_url,
            is_running=campaign.is_running
        )
        db.add(db_campaign)
        db.flush()

        # Process payouts
        for payout in campaign.payouts:
            country_details = get_country_details(payout.country)
            if not country_details:
                raise ValueError(f"Country details not found for: {payout.country}")
                
            db_payout = Payout(
                country=payout.country,
                amount=payout.amount,
                campaign_id=db_campaign.id
            )
            db.add(db_payout)

        db.commit()
        db.refresh(db_campaign)
        return db_campaign

    def get_campaigns(self, db: Session, skip: int = 0, limit: int = 100, filters: Dict[str, Any] = None) -> List[Campaign]:
        query = db.query(Campaign)
        if filters:
            if filters.get("title"):
                query = query.filter(Campaign.title.ilike(f"%{filters['title']}%"))
            if filters.get("landing_url"):
                query = query.filter(Campaign.landing_url.ilike(f"%{filters['landing_url']}%"))
            if filters.get("is_running") is not None:
                query = query.filter(Campaign.is_running == filters["is_running"])
        
        return query.offset(skip).limit(limit).all()

# Create singleton instance
campaign_service = CampaignService()