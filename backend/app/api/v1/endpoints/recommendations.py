from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, or_, and_
from app.db.session import get_db
from app.models.models import User, Content, Recommendation
from app.schemas.schemas import Recommendation as RecommendationSchema, RecommendationCreate
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

@router.get("/", response_model=List[RecommendationSchema])
async def get_recommendations(
    current_user: User = Depends(get_current_user),
    content_type: Optional[str] = None,
    genre: Optional[str] = None,
    language: Optional[str] = None,
    is_public: Optional[bool] = None,
    sort_by: Optional[str] = "created_at",
    session: Session = Depends(get_db)
) -> Any:
    # Build the base query
    base_query = select(Recommendation).where(Recommendation.user_id == current_user.id)
    
    # Add filters
    if content_type:
        base_query = base_query.join(Content).where(Content.content_type == content_type)
    if genre:
        base_query = base_query.join(Content).where(Content.genres.ilike(f"%{genre}%"))
    if language:
        base_query = base_query.join(Content).where(Content.language == language)
    if is_public is not None:
        base_query = base_query.where(Recommendation.is_public == is_public)
    
    # Add sorting
    if sort_by == "created_at":
        base_query = base_query.order_by(Recommendation.created_at.desc())
    elif sort_by == "imdb_rating":
        base_query = base_query.join(Content).order_by(Content.imdb_rating.desc())
    
    # Execute the query
    results = session.exec(base_query).all()
    return results

@router.get("/public", response_model=List[RecommendationSchema])
async def get_public_recommendations(
    content_type: Optional[str] = None,
    genre: Optional[str] = None,
    language: Optional[str] = None,
    sort_by: Optional[str] = "created_at",
    session: Session = Depends(get_db)
) -> Any:
    # Build the base query
    base_query = select(Recommendation).where(Recommendation.is_public == True)
    
    # Add filters
    if content_type:
        base_query = base_query.join(Content).where(Content.content_type == content_type)
    if genre:
        base_query = base_query.join(Content).where(Content.genres.ilike(f"%{genre}%"))
    if language:
        base_query = base_query.join(Content).where(Content.language == language)
    
    # Add sorting
    if sort_by == "created_at":
        base_query = base_query.order_by(Recommendation.created_at.desc())
    elif sort_by == "imdb_rating":
        base_query = base_query.join(Content).order_by(Content.imdb_rating.desc())
    
    # Execute the query
    results = session.exec(base_query).all()
    return results

@router.post("/", response_model=RecommendationSchema)
async def create_recommendation(
    recommendation: RecommendationCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
) -> Any:
    # Check if content exists
    content = session.exec(select(Content).where(Content.id == recommendation.content_id)).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    # Check if already recommended
    existing_recommendation = session.exec(
        select(Recommendation)
        .where(Recommendation.user_id == current_user.id)
        .where(Recommendation.content_id == recommendation.content_id)
    ).first()
    if existing_recommendation:
        raise HTTPException(status_code=400, detail="Content already recommended")
    
    db_recommendation = Recommendation(
        user_id=current_user.id,
        content_id=recommendation.content_id,
        is_public=recommendation.is_public,
        note=recommendation.note
    )
    session.add(db_recommendation)
    session.commit()
    session.refresh(db_recommendation)
    return db_recommendation

@router.put("/{recommendation_id}", response_model=RecommendationSchema)
async def update_recommendation(
    recommendation_id: int,
    recommendation: RecommendationCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
) -> Any:
    db_recommendation = session.exec(
        select(Recommendation)
        .where(Recommendation.id == recommendation_id)
        .where(Recommendation.user_id == current_user.id)
    ).first()
    if not db_recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    db_recommendation.is_public = recommendation.is_public
    db_recommendation.note = recommendation.note
    
    session.commit()
    session.refresh(db_recommendation)
    return db_recommendation

@router.delete("/{recommendation_id}")
async def delete_recommendation(
    recommendation_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
) -> Any:
    db_recommendation = session.exec(
        select(Recommendation)
        .where(Recommendation.id == recommendation_id)
        .where(Recommendation.user_id == current_user.id)
    ).first()
    if not db_recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    session.delete(db_recommendation)
    session.commit()
    return {"message": "Recommendation deleted"} 