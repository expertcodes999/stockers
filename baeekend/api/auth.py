from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.database import get_db
from service.auth import auth_service
from schemas.auth import UserCreate, UserLogin, Token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = auth_service.create_user(db, user)
    access_token = auth_service.create_access_token({"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/token", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = auth_service.authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token = auth_service.create_access_token({"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}