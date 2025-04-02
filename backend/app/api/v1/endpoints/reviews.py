from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.db.session import get_db
from app.models.models import User, Content, Review
from app.schemas.schemas import Review as ReviewSchema, ReviewCreate, ReviewResponse
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

@router.get("/", response_model=List[ReviewResponse])
def get_reviews(
    session: Session = Depends(get_db),
) -> Any:
    reviews = session.exec(select(Review)).all()
    return reviews

@router.post("/", response_model=ReviewResponse)
def create_review(
    review: ReviewCreate,
    session: Session = Depends(get_db),
) -> Any:
    db_review = Review(**review.dict())
    session.add(db_review)
    session.commit()
    session.refresh(db_review)
    return db_review

@router.get("/{review_id}", response_model=ReviewResponse)
def get_review(
    review_id: int,
    session: Session = Depends(get_db),
) -> Any:
    review = session.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review

@router.put("/{review_id}", response_model=ReviewResponse)
def update_review(
    review_id: int,
    review: ReviewCreate,
    session: Session = Depends(get_db),
) -> Any:
    db_review = session.get(Review, review_id)
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    for key, value in review.dict().items():
        setattr(db_review, key, value)
    
    session.commit()
    session.refresh(db_review)
    return db_review

@router.delete("/{review_id}")
def delete_review(
    review_id: int,
    session: Session = Depends(get_db),
) -> Any:
    review = session.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    session.delete(review)
    session.commit()
    return {"message": "Review deleted successfully"} 