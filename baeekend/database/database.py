from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from enum import Enum
from pydantic import BaseModel, ValidationError
import json
import os
import logging
from typing import List, Optional, Dict, Type
from functools import lru_cache

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------
# Country Data Handling
# --------------------------

class CountrySchema(BaseModel):
    """Pydantic model for validating country data"""
    COUNTRY: str
    COUNTRY_CODE: str
    CURRENCY_CODE: str
    NAME_OF_CURRENCY: str

class CountryManager:
    """Singleton class for managing country data"""
    _instance = None
    _data_loaded = False
    _countries: Dict[str, CountrySchema] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_data()
        return cls._instance

    def _load_data(self) -> None:
        """Load and validate country data from JSON file"""
        try:
            filepath = os.path.join(os.path.dirname(__file__), 'countries.json')
            logger.info(f"Loading countries from: {filepath}")
            
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"Countries file not found: {filepath}")

            with open(filepath) as f:
                raw_data = json.load(f)
                self._validate_and_store(raw_data.get('countries', []))
                self._data_loaded = True

        except Exception as e:
            logger.error(f"Failed to load country data: {str(e)}")
            raise

    def _validate_and_store(self, raw_data: List[Dict]) -> None:
        """Validate and store country data using Pydantic model"""
        self._countries.clear()
        for item in raw_data:
            try:
                country = CountrySchema(**item)
                self._countries[country.COUNTRY_CODE] = country
            except ValidationError as e:
                logger.warning(f"Skipping invalid country data: {str(e)}")

    @property
    @lru_cache(maxsize=None)
    def countries(self) -> Dict[str, CountrySchema]:
        """Get validated country data with caching"""
        if not self._data_loaded:
            self._load_data()
        return self._countries

    def get_country(self, code: str) -> Optional[CountrySchema]:
        """Get single country by code"""
        return self.countries.get(code.upper())

# --------------------------
# Country Enum Implementation
# --------------------------

class CountryMeta(type):
    """Metaclass for dynamic Country enum creation"""
    def __getattr__(cls, name):
        country = country_manager.get_country(name)
        if country:
            return country.COUNTRY_CODE
        raise AttributeError(f"No country with code {name}")

class Country(str, Enum, metaclass=CountryMeta):
    """Dynamic country enum based on loaded data"""
    @classmethod
    def _missing_(cls, value):
        if country := country_manager.get_country(value):
            return cls(country.COUNTRY_CODE)
        raise ValueError(f"Invalid country code: {value}")

    @classmethod
    def get_details(cls, code: str) -> Optional[CountrySchema]:
        """Get full country details by code"""
        return country_manager.get_country(code)

# --------------------------
# Database Configuration
# --------------------------

load_dotenv()
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Database session generator"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize country manager at module level
country_manager = CountryManager()