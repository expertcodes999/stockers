from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from enum import Enum
from pydantic import BaseModel
import json
import os
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def load_countries():
    try:
        filepath = os.path.join(os.path.dirname(__file__), 'countries.json')
        logger.debug(f"Loading countries from: {filepath}")
        
        with open(filepath) as f:
            data = json.load(f)
            countries = data['countries']
            logger.debug(f"Loaded {len(countries)} countries")
            return countries
    except Exception as e:
        logger.error(f"Failed to load countries: {e}")
        raise

# Load countries first
COUNTRIES_DATA = load_countries()
logger.debug(f"Countries data loaded: {COUNTRIES_DATA[:2]}")  # Show first two countries

# Create Country enum with initial member to prevent empty enum
class Country(str, Enum):
    # Add initial member
    AFG = "AFG"
    
    @classmethod
    def _missing_(cls, value):
        for country in COUNTRIES_DATA:
            if country['COUNTRY_CODE'] == value:
                return cls(value)
        raise ValueError(f"{value} is not a valid Country code")

# Add country codes to enum
for country in COUNTRIES_DATA:
    code = country['COUNTRY_CODE']
    logger.debug(f"Adding country code: {code}")
    if not hasattr(Country, code):
        setattr(Country, code, code)

logger.debug(f"Country enum members: {list(Country.__members__.keys())}")

def get_country_details(country_code: str):
    """Get full country details by country code"""
    return next(
        (country for country in COUNTRIES_DATA 
         if country['COUNTRY_CODE'] == country_code),
        None
    )

# Database setup
load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class CountryData(BaseModel):
    COUNTRY: str
    COUNTRY_CODE: str
    CURRENCY_CODE: str
    NAME_OF_CURRENCY: str