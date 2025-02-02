import json
import os
import hashlib
import secrets
import bcrypt
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, Enum as SQLAlchemyEnum, DateTime
from sqlalchemy.orm import relationship
from database.database import Base, Country
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String(60))  # bcrypt hash is always 60 chars
    campaigns = relationship("Campaign", back_populates="owner")
    
    def set_password(self, password: str):
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        self.hashed_password = hashed.decode('utf-8')
        
    def check_password(self, password: str) -> bool:
        password_bytes = password.encode('utf-8')
        hashed_bytes = self.hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)

class Campaign(Base):
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    landing_url = Column(String, nullable=False)
    is_running = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    country = Column(SQLAlchemyEnum(Country), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="campaigns")
    payouts = relationship("Payout", back_populates="campaign", cascade="all, delete-orphan")

class Payout(Base):
    __tablename__ = "payouts"
    
    id = Column(Integer, primary_key=True, index=True)
    country = Column(SQLAlchemyEnum(Country), nullable=False)
    amount = Column(Float, nullable=False)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"))
    campaign = relationship("Campaign", back_populates="payouts")