from typing import Any, List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, or_, and_
from app.db.session import get_db
from app.models.models import User, Content, ContentType
from app.schemas.schemas import (
    Content as ContentSchema,
    ContentCreate,
    ContentResponse,
    CreditsResponse,
    SearchResponse,
    SimilarContentResponse,
    Genre
)
from app.api.v1.endpoints.auth import oauth2_scheme
from app.core import security
from datetime import datetime
from app.services.content_service import content_service
from app.core.auth import get_current_user

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

@router.get("/search", response_model=SearchResponse)
async def search_content(
    query: str = Query(..., min_length=1),
    page: int = Query(1, description="Page number"),
    current_user: User = Depends(get_current_user)
):
    """
    Search for TV shows
    """
    try:
        results = await content_service.search_content(
            query=query,
            page=page
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/shows/{tvmaze_id}", response_model=ContentResponse)
async def get_content_by_id(
    tvmaze_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed show information by TVMaze ID
    """
    try:
        content = await content_service.get_content_by_id(tvmaze_id, "tv")
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
        return content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/shows/{tvmaze_id}/credits", response_model=CreditsResponse)
async def get_cast_and_crew(
    tvmaze_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get cast and crew information for a show
    """
    try:
        credits = await content_service.get_cast_and_crew(tvmaze_id, "tv")
        return credits
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/shows/{tvmaze_id}/similar", response_model=SimilarContentResponse)
async def get_similar_content(
    tvmaze_id: str,
    page: int = Query(1, description="Page number"),
    current_user: User = Depends(get_current_user)
):
    """
    Get similar shows based on genres and other attributes
    """
    try:
        similar = await content_service.get_similar_content(
            tvmaze_id=tvmaze_id,
            content_type="tv",
            page=page
        )
        return similar
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/genres", response_model=List[Genre])
async def get_genres(
    current_user: User = Depends(get_current_user)
):
    """
    Get list of available genres
    """
    try:
        genres = await content_service.get_genres("tv")
        return genres
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trending", response_model=List[ContentResponse])
async def get_trending_content(
    current_user: User = Depends(get_current_user)
):
    """
    Get trending TV shows
    """
    try:
        trending = await content_service.get_trending_content("tv")
        return trending
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cache/{tvmaze_id}")
async def clear_content_cache(
    tvmaze_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Clear content cache for a specific show or all shows
    """
    try:
        await content_service.clear_content_cache(tvmaze_id)
        return {"message": "Cache cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/db/{content_id}", response_model=ContentSchema)
async def get_content_details(
    content_id: int,
    session: Session = Depends(get_db)
) -> Any:
    """
    Get content details from database
    """
    content = session.get(Content, content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return content

@router.post("/db/", response_model=ContentSchema)
async def create_content(
    content: ContentCreate,
    session: Session = Depends(get_db)
) -> Any:
    """
    Create new content in database
    """
    # Check if content already exists
    existing_content = session.exec(
        select(Content).where(Content.tvmaze_id == content.tvmaze_id)
    ).first()
    
    if existing_content:
        raise HTTPException(
            status_code=400,
            detail="Content with this TVMaze ID already exists"
        )
    
    db_content = Content(**content.dict())
    session.add(db_content)
    session.commit()
    session.refresh(db_content)
    return db_content 