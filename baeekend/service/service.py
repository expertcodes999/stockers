import json
import os
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from models.models import Campaign, Payout
from schemas.schema import CampaignCreate, Campaign as CampaignSchema, CampaignUpdate, PayoutCreate, PayoutUpdate
from database.database import get_country_details, Country
from sqlalchemy import and_

class CampaignService:
   
    def create_campaign(self, db: Session, campaign: CampaignCreate) -> CampaignSchema:
        # Validate country enum
        if not isinstance(campaign.country, Country):
            raise ValueError(f"Invalid campaign country: {campaign.country}")
            
        # Create campaign with country
        db_campaign = Campaign(
            title=campaign.title,
            landing_url=campaign.landing_url,
            is_running=campaign.is_running,
            country=campaign.country
        )
        db.add(db_campaign)
        db.flush()

        # Validate and process payouts
        seen_countries = set()
        for payout in campaign.payouts:
            if not isinstance(payout.country, Country):
                raise ValueError(f"Invalid payout country: {payout.country}")
            if payout.country in seen_countries:
                raise ValueError(f"Duplicate payout country: {payout.country}")
            seen_countries.add(payout.country)
            
            db_payout = Payout(
                country=payout.country,
                amount=payout.amount,
                campaign_id=db_campaign.id
            )
            db.add(db_payout)

        try:
            db.commit()
            db.refresh(db_campaign)
            return db_campaign
        except Exception as e:
            db.rollback()
            raise ValueError(f"Error creating campaign: {str(e)}")

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

    def get_campaign(self, db: Session, campaign_id: int) -> Optional[Campaign]:
        return db.query(Campaign).filter(Campaign.id == campaign_id).first()

    def update_campaign(self, db: Session, campaign_id: int, campaign_update: CampaignUpdate) -> Optional[Campaign]:
        db_campaign = self.get_campaign(db, campaign_id)
        if not db_campaign:
            return None
            
        update_data = campaign_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field != "payouts":
                setattr(db_campaign, field, value)
        
        if campaign_update.payouts:
            # Clear existing payouts
            db_campaign.payouts = []
            # Add new payouts
            for payout in campaign_update.payouts:
                db_payout = Payout(
                    country=payout.country,
                    amount=payout.amount,
                    campaign_id=db_campaign.id
                )
                db.add(db_payout)
        
        try:
            db.commit()
            db.refresh(db_campaign)
            return db_campaign
        except Exception as e:
            db.rollback()
            raise ValueError(f"Error updating campaign: {str(e)}")

    def delete_campaign(self, db: Session, campaign_id: int) -> bool:
        db_campaign = self.get_campaign(db, campaign_id)
        if not db_campaign:
            return False
        db.delete(db_campaign)
        db.commit()
        return True

class PayoutService:
    def create_payout(self, db: Session, campaign_id: int, payout: PayoutCreate) -> Payout:
        if not payout.country:
            raise ValueError("Country is required")

        db_payout = Payout(
            country=payout.country,  # Ensure country is set first
            amount=payout.amount,
            campaign_id=campaign_id
        )
        db.add(db_payout)
        
        try:
            db.commit()
            db.refresh(db_payout)
            return db_payout
        except Exception as e:
            db.rollback()
            raise ValueError(f"Error creating payout: {str(e)}")

    def update_payout(self, db: Session, payout_id: int, payout_update: PayoutUpdate) -> Optional[Payout]:
        db_payout = self.get_payout(db, payout_id)
        if not db_payout:
            return None

        if not isinstance(payout_update.country, Country):
            raise ValueError(f"Invalid country: {payout_update.country}")

        # Check for duplicate if country is being changed
        if db_payout.country != payout_update.country:
            existing = db.query(Payout).filter(
                and_(
                    Payout.campaign_id == db_payout.campaign_id,
                    Payout.country == payout_update.country,
                    Payout.id != payout_id
                )
            ).first()
            if existing:
                raise ValueError(f"Payout for country {payout_update.country} already exists")

        db_payout.country = payout_update.country
        db_payout.amount = payout_update.amount
        
        try:
            db.commit()
            db.refresh(db_payout)
            return db_payout
        except Exception as e:
            db.rollback()
            raise ValueError(f"Error updating payout: {str(e)}")

    def get_payout(self, db: Session, payout_id: int) -> Optional[Payout]:
        return db.query(Payout).filter(Payout.id == payout_id).first()

    def get_campaign_payouts(self, db: Session, campaign_id: int) -> List[Payout]:
        return db.query(Payout).filter(Payout.campaign_id == campaign_id).all()

    def delete_payout(self, db: Session, payout_id: int) -> bool:
        db_payout = self.get_payout(db, payout_id)
        if not db_payout:
            return False
            
        # Prevent deleting last payout
        campaign_payouts = self.get_campaign_payouts(db, db_payout.campaign_id)
        if len(campaign_payouts) <= 1:
            raise ValueError("Cannot delete the last payout from a campaign")
            
        try:
            db.delete(db_payout)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise ValueError(f"Error deleting payout: {str(e)}")

# Create singleton instances
campaign_service = CampaignService()
payout_service = PayoutService()