# backend/tests/test_campaigns.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app import models, schemas, services

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base = declarative_base()
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_create_campaign(db_session):
    campaign_data = schemas.CampaignCreate(
        title="Test Campaign",
        landing_url="https://example.com",
        payouts={"US": 10.0, "UK": 15.0}
    )
    campaign = services.create_campaign(db_session, campaign_data)
    assert campaign.title == "Test Campaign"
    assert campaign.landing_url == "https://example.com"
    assert campaign.payouts == {"US": 10.0, "UK": 15.0}