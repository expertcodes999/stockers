from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from ..database.database import Base, Country

class Campaign(Base):
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    landing_url = Column(String, nullable=False)
    is_running = Column(Boolean, default=False)
    payouts = relationship("Payout", back_populates="campaign")

class Payout(Base):
    __tablename__ = "payouts"
    
    id = Column(Integer, primary_key=True, index=True)
    country = Column(SQLAlchemyEnum(Country), nullable=False)
    amount = Column(Float, nullable=False)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    campaign = relationship("Campaign", back_populates="payouts")