import json
import os
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from database.database import Country

class PayoutBase(BaseModel):
    country: str = Field(
        ...,
        description="Country code (e.g. AFG, USA, GBR)",
        example="AFG"
    )
    amount: float = Field(
        ..., 
        gt=0,
        example=100.00
    )

    @validator('country')
    def validate_country(cls, v):
        try:
            return Country(v)
        except ValueError:
            raise ValueError(f"Invalid country code: {v}")

    class Config:
        json_schema_extra = {
            "example": {
                "country": "AFG",
                "amount": 100.00
            }
        }

class PayoutCreate(PayoutBase):
    pass

class Payout(PayoutBase):
    id: int
    campaign_id: int
    
    model_config = {
        "from_attributes": True
    }

class PayoutUpdate(BaseModel):
    amount: float = Field(..., gt=0)
    country: Country 

    class Config:
        json_schema_extra = {
            "example": {
                "amount": 100.00,
                "country": "US"  # Example of valid country code
            }
        }

class CampaignBase(BaseModel):
    title: str = Field(..., example="Test Campaign")
    landing_url: str = Field(..., example="https://example.com")
    is_running: bool = Field(default=False)
    country: str = Field(
        ...,
        description="Country code (e.g. AFG, USA, GBR)",
        example="AFG"
    )

    @validator('country')
    def validate_country(cls, v):
        try:
            return Country(v)
        except ValueError:
            raise ValueError(f"Invalid country code: {v}")

class CampaignCreate(CampaignBase):
    payouts: List[PayoutCreate]

class Campaign(CampaignBase):
    id: int
    payouts: List[Payout]
    
    model_config = {
        "from_attributes": True
    }

class CampaignUpdate(BaseModel):
    title: Optional[str] = None
    landing_url: Optional[str] = None
    is_running: Optional[bool] = None
    payouts: Optional[List[PayoutCreate]] = None