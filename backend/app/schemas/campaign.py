# schemas/campaign.py
from pydantic import BaseModel
from typing import List


class CampaignBase(BaseModel):
    title: str
    landing_url: str
    is_running: bool = False
    payouts: List[PayoutBase]

class CampaignCreate(CampaignBase):
    pass

class Campaign(CampaignBase):
    id: int