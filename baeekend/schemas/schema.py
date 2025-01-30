from pydantic import BaseModel, Field
from typing import List
from ..database.database import Country

class PayoutBase(BaseModel):
    country: Country
    amount: float = Field(..., gt=0)

class PayoutCreate(PayoutBase):
    pass

class Payout(PayoutBase):
    id: int
    campaign_id: int
    
    model_config = {
        "from_attributes": True
    }

class CampaignBase(BaseModel):
    title: str
    landing_url: str
    is_running: bool = False

class CampaignCreate(CampaignBase):
    payouts: List[PayoutCreate]

class Campaign(CampaignBase):
    id: int
    payouts: List[Payout]
    
    model_config = {
        "from_attributes": True
    }