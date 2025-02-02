import json
import os
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from database.database import Country

class PayoutBase(BaseModel):
    amount: float = Field(..., gt=0)
    country: Country  # Changed from country_code to country

    class Config:
        use_enum_values = True

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
    title: str = Field(..., min_length=1)
    landing_url: str
    is_running: bool = Field(default=False)
    country: Country  # Changed from str to Country

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

class CountryManager:
    _instance = None
    _initialized = False
    countries_data: List = []
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self._load_countries()

    def _load_countries(self) -> bool:
        try:
            filepath = os.path.join(os.path.dirname(__file__), 'countries.json')
            logger.info(f"Loading countries from: {filepath}")
            
            if not os.path.exists(filepath):
                logger.error(f"Countries file not found: {filepath}")
                return False

            with open(filepath) as f:
                data = json.load(f)
                self.countries_data = [
                    country for country in data['countries']
                    if all(key in country for key in ['COUNTRY', 'COUNTRY_CODE'])
                    and country['COUNTRY_CODE'] and country['COUNTRY_CODE'] != "-"
                ]
                
                # Dynamically add countries to enum
                for country in self.countries_data:
                    code = country['COUNTRY_CODE']
                    if not hasattr(Country, code):
                        setattr(Country, code, code)
                
                logger.info(f"Successfully loaded {len(self.countries_data)} countries")
                return True
        except Exception as e:
            logger.error(f"Failed to load countries: {str(e)}")
            return False

    def verify_countries_loaded(self) -> bool:
        return bool(self.countries_data)