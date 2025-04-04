from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.db.session import get_db
from app.models.models import User, Content, Rating
from app.schemas.schemas import Rating as RatingSchema, RatingCreate, RatingResponse
from app.api.v1.endpoints.auth import oauth2_scheme
from app.core import security
from datetime import datetime

router = APIRouter()

async def get_current_user(
    session: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = security.decode_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
    
    user = session.exec(select(User).where(User.email == email)).first()
    if user is None:
        raise credentials_exception
    return user

@router.get("/", response_model=List[RatingResponse])
def get_ratings(
    session: Session = Depends(get_db),
) -> Any:
    ratings = session.exec(select(Rating)).all()
    return ratings

@router.post("/", response_model=RatingResponse)
def create_rating(
    rating: RatingCreate,
    session: Session = Depends(get_db),
) -> Any:
    db_rating = Rating(**rating.dict())
    session.add(db_rating)
    session.commit()
    session.refresh(db_rating)
    return db_rating

@router.get("/{rating_id}", response_model=RatingResponse)
def get_rating(
    rating_id: int,
    session: Session = Depends(get_db),
) -> Any:
    rating = session.get(Rating, rating_id)
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    return rating

@router.put("/{rating_id}", response_model=RatingResponse)
def update_rating(
    rating_id: int,
    rating: RatingCreate,
    session: Session = Depends(get_db),
) -> Any:
    db_rating = session.get(Rating, rating_id)
    if not db_rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    
    for key, value in rating.dict().items():
        setattr(db_rating, key, value)
    
    session.commit()
    session.refresh(db_rating)
    return db_rating

@router.delete("/{rating_id}")
def delete_rating(
    rating_id: int,
    session: Session = Depends(get_db),
) -> Any:
    rating = session.get(Rating, rating_id)
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    
    session.delete(rating)
    session.commit()
    return {"message": "Rating deleted successfully"} 