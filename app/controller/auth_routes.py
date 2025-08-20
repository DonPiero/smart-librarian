from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from app.models.schemas import UserCreate, UserLogin
from app.services.db_connection import SessionLocal
from app.services.user_service import (
    create_user,
    get_user_by_username,
    verify_password
)
from app.auth.jwt_handler import create_token

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register")
def register(data: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_username(db, data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    user = create_user(db, data.username, data.password)

    return {"message": f"User '{user.username}' created successfully"}


@router.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = get_user_by_username(db, data.username)
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    token = create_token({"sub": user.username})

    return {"access_token": token,
            "token_type": "bearer"}
