import json
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.database import engine, Base, country_manager, Country
from api.routes import router as campaign_router
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="Campaign Management API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)
app.include_router(campaign_router)

@app.on_event("startup")
async def startup_event():
    """Verify countries are loaded before starting the app"""
    countries = country_manager.get_countries()
    if not countries:
        raise RuntimeError("Failed to load countries")
    logger.info(f"Successfully loaded {len(countries)} countries")

@app.get("/")
async def root():
    return {"status": "healthy", "message": "Campaign Management API"}