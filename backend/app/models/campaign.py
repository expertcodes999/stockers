# models/campaign.py
from sqlalchemy import Column, Integer, String, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship

class Campaign(Base):
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    landing_url = Column(String, nullable=False)
    is_running = Column(Boolean, default=False)
    payouts = relationship("Payout", back_populates="campaign")
