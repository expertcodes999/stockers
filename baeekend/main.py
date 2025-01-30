from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database.database import engine, Base
from .api.routes import router as campaign_router

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

@app.get("/")
async def root():
    return {"status": "healthy", "message": "Campaign Management API"}