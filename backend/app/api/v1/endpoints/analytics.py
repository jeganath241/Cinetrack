from typing import Any, List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, or_, and_, func
from app.db.session import get_db
from app.models.models import User, Content, WatchHistory, Analytics
from app.schemas.schemas import (
    WatchHistory as WatchHistorySchema,
    WatchHistoryCreate,
    AnalyticsCreate,
    AnalyticsResponse
)
from app.api.v1.endpoints.auth import oauth2_scheme
from app.core import security
from datetime import datetime, timedelta
import json

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

@router.post("/history", response_model=WatchHistorySchema)
async def add_watch_history(
    history: WatchHistoryCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
) -> Any:
    # Check if content exists
    content = session.exec(select(Content).where(Content.id == history.content_id)).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    db_history = WatchHistory(
        **history.dict(),
        user_id=current_user.id
    )
    session.add(db_history)
    session.commit()
    session.refresh(db_history)
    return db_history

@router.get("/history", response_model=List[WatchHistorySchema])
async def get_watch_history(
    current_user: User = Depends(get_current_user),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    content_type: Optional[str] = None,
    session: Session = Depends(get_db)
) -> Any:
    query = select(WatchHistory).where(WatchHistory.user_id == current_user.id)
    
    if start_date:
        query = query.where(WatchHistory.watched_at >= start_date)
    if end_date:
        query = query.where(WatchHistory.watched_at <= end_date)
    if content_type:
        query = query.join(Content).where(Content.content_type == content_type)
    
    results = session.exec(query).all()
    return results

@router.get("/stats/weekly", response_model=Dict[str, Any])
async def get_weekly_stats(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
) -> Any:
    # Get the start of the current week
    today = datetime.utcnow()
    start_of_week = today - timedelta(days=today.weekday())
    
    # Get watch history for the current week
    weekly_history = session.exec(
        select(WatchHistory)
        .where(WatchHistory.user_id == current_user.id)
        .where(WatchHistory.watched_at >= start_of_week)
    ).all()
    
    # Calculate stats
    total_minutes = sum(wh.duration_minutes for wh in weekly_history)
    total_movies = len([wh for wh in weekly_history if wh.content.content_type == "movie"])
    total_series = len([wh for wh in weekly_history if wh.content.content_type == "series"])
    total_anime = len([wh for wh in weekly_history if wh.content.content_type == "anime"])
    
    # Get genre distribution
    genre_counts = {}
    for wh in weekly_history:
        if wh.content.genres:
            for genre in wh.content.genres.split(','):
                genre = genre.strip()
                genre_counts[genre] = genre_counts.get(genre, 0) + 1
    
    return {
        "total_minutes": total_minutes,
        "total_movies": total_movies,
        "total_series": total_series,
        "total_anime": total_anime,
        "genre_distribution": genre_counts
    }

@router.get("/stats/monthly", response_model=Dict[str, Any])
async def get_monthly_stats(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
) -> Any:
    # Get the start of the current month
    today = datetime.utcnow()
    start_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Get watch history for the current month
    monthly_history = session.exec(
        select(WatchHistory)
        .where(WatchHistory.user_id == current_user.id)
        .where(WatchHistory.watched_at >= start_of_month)
    ).all()
    
    # Calculate stats
    total_minutes = sum(wh.duration_minutes for wh in monthly_history)
    total_movies = len([wh for wh in monthly_history if wh.content.content_type == "movie"])
    total_series = len([wh for wh in monthly_history if wh.content.content_type == "series"])
    total_anime = len([wh for wh in monthly_history if wh.content.content_type == "anime"])
    
    # Get genre distribution
    genre_counts = {}
    for wh in monthly_history:
        if wh.content.genres:
            for genre in wh.content.genres.split(','):
                genre = genre.strip()
                genre_counts[genre] = genre_counts.get(genre, 0) + 1
    
    return {
        "total_minutes": total_minutes,
        "total_movies": total_movies,
        "total_series": total_series,
        "total_anime": total_anime,
        "genre_distribution": genre_counts
    }

@router.get("/stats/yearly", response_model=Dict[str, Any])
async def get_yearly_stats(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
) -> Any:
    # Get the start of the current year
    today = datetime.utcnow()
    start_of_year = today.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Get watch history for the current year
    yearly_history = session.exec(
        select(WatchHistory)
        .where(WatchHistory.user_id == current_user.id)
        .where(WatchHistory.watched_at >= start_of_year)
    ).all()
    
    # Calculate stats
    total_minutes = sum(wh.duration_minutes for wh in yearly_history)
    total_movies = len([wh for wh in yearly_history if wh.content.content_type == "movie"])
    total_series = len([wh for wh in yearly_history if wh.content.content_type == "series"])
    total_anime = len([wh for wh in yearly_history if wh.content.content_type == "anime"])
    
    # Get genre distribution
    genre_counts = {}
    for wh in yearly_history:
        if wh.content.genres:
            for genre in wh.content.genres.split(','):
                genre = genre.strip()
                genre_counts[genre] = genre_counts.get(genre, 0) + 1
    
    # Get top 5 movies by rating
    top_movies = session.exec(
        select(WatchHistory)
        .join(Content)
        .where(WatchHistory.user_id == current_user.id)
        .where(WatchHistory.watched_at >= start_of_year)
        .where(Content.content_type == "movie")
        .order_by(Content.imdb_rating.desc())
        .limit(5)
    ).all()
    
    return {
        "total_minutes": total_minutes,
        "total_movies": total_movies,
        "total_series": total_series,
        "total_anime": total_anime,
        "genre_distribution": genre_counts,
        "top_movies": [
            {
                "title": wh.content.title,
                "rating": wh.content.imdb_rating,
                "watched_at": wh.watched_at
            }
            for wh in top_movies
        ]
    }

@router.get("/stats/heatmap", response_model=Dict[str, Any])
async def get_genre_heatmap(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
) -> Any:
    # Get all watch history
    history = session.exec(
        select(WatchHistory)
        .where(WatchHistory.user_id == current_user.id)
    ).all()
    
    # Calculate genre heatmap
    genre_heatmap = {}
    for wh in history:
        if wh.content.genres:
            for genre in wh.content.genres.split(','):
                genre = genre.strip()
                if genre not in genre_heatmap:
                    genre_heatmap[genre] = {
                        "count": 0,
                        "total_minutes": 0,
                        "movies": 0,
                        "series": 0,
                        "anime": 0
                    }
                genre_heatmap[genre]["count"] += 1
                genre_heatmap[genre]["total_minutes"] += wh.duration_minutes
                if wh.content.content_type == "movie":
                    genre_heatmap[genre]["movies"] += 1
                elif wh.content.content_type == "series":
                    genre_heatmap[genre]["series"] += 1
                elif wh.content.content_type == "anime":
                    genre_heatmap[genre]["anime"] += 1
    
    return genre_heatmap

@router.get("/", response_model=List[AnalyticsResponse])
def get_analytics(
    session: Session = Depends(get_db),
) -> Any:
    analytics = session.exec(select(Analytics)).all()
    return analytics

@router.post("/", response_model=AnalyticsResponse)
def create_analytics(
    analytics: AnalyticsCreate,
    session: Session = Depends(get_db),
) -> Any:
    db_analytics = Analytics(**analytics.dict())
    session.add(db_analytics)
    session.commit()
    session.refresh(db_analytics)
    return db_analytics

@router.get("/{analytics_id}", response_model=AnalyticsResponse)
def get_analytics_item(
    analytics_id: int,
    session: Session = Depends(get_db),
) -> Any:
    analytics = session.get(Analytics, analytics_id)
    if not analytics:
        raise HTTPException(status_code=404, detail="Analytics not found")
    return analytics

@router.put("/{analytics_id}", response_model=AnalyticsResponse)
def update_analytics(
    analytics_id: int,
    analytics: AnalyticsCreate,
    session: Session = Depends(get_db),
) -> Any:
    db_analytics = session.get(Analytics, analytics_id)
    if not db_analytics:
        raise HTTPException(status_code=404, detail="Analytics not found")
    
    for key, value in analytics.dict().items():
        setattr(db_analytics, key, value)
    
    session.commit()
    session.refresh(db_analytics)
    return db_analytics

@router.delete("/{analytics_id}")
def delete_analytics(
    analytics_id: int,
    session: Session = Depends(get_db),
) -> Any:
    analytics = session.get(Analytics, analytics_id)
    if not analytics:
        raise HTTPException(status_code=404, detail="Analytics not found")
    
    session.delete(analytics)
    session.commit()
    return {"message": "Analytics deleted successfully"} 