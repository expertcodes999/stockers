from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from enum import Enum
from pydantic import BaseModel
import json
import os

# Load countries configuration
def load_countries():
    with open(os.path.join(os.path.dirname(__file__), 'countries.json')) as f:
        return json.load(f)['countries']

COUNTRIES_DATA = load_countries()

# Create dynamic Country Enum
class Country(str, Enum):
    @classmethod
    def _missing_(cls, value):
        for country in COUNTRIES_DATA:
            if country['COUNTRY_CODE'] == value:
                return cls(value)
        raise ValueError(f"{value} is not a valid Country code")

# Dynamically add country codes to the Enum
for country in COUNTRIES_DATA:
    setattr(Country, country['COUNTRY_CODE'], country['COUNTRY_CODE'])

def get_country_details(country_code: str):
    """Get full country details by country code"""
    return next(
        (country for country in COUNTRIES_DATA 
         if country['COUNTRY_CODE'] == country_code),
        None
    )

def get_currency_for_country(country_code: str):
    """Get currency code for a country"""
    country = get_country_details(country_code)
    return country['CURRENCY_CODE'] if country else None

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