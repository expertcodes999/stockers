# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from app.core.database import engine, Base

# Create FastAPI app instance
app = FastAPI(title="Campaign Management API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
# Base.metadata.create_all(bind=engine)

# Health check endpoint
@app.get("/")
async def root():
    return {"status": "healthy", "message": "Campaign Management API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)