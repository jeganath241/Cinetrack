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
from app.core.auth import get_current_user
from datetime import datetime
from app.services.content_service import content_service
from app.api.v1.endpoints.auth import get_current_user_optional

router = APIRouter()

@router.get("/search", response_model=SearchResponse)
async def search_content(
    query: str = Query(..., min_length=1),
    page: int = Query(1, description="Page number"),
    current_user: Optional[User] = None
):
    """
    Search for TV shows (public endpoint)
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

@router.get("/search")
async def search_content(
    query: str,
    content_type: Optional[str] = None,
    language: Optional[str] = None,
    page: int = Query(1, ge=1),
    current_user: Optional[User] = Depends(get_current_user_optional)
) -> Any:
    """
    Search for content by title
    """
    return await content_service.search_content(query, content_type, language, page)

@router.get("/show/{show_id}")
async def get_show_details(
    show_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional)
) -> Any:
    """
    Get detailed information about a show
    """
    result = await content_service.get_show_details(show_id)
    if not result:
        raise HTTPException(status_code=404, detail="Show not found")
    return result

@router.get("/schedule")
async def get_schedule(
    country: str = "US",
    date: Optional[str] = None,
    current_user: Optional[User] = Depends(get_current_user_optional)
) -> Any:
    """
    Get TV schedule for a specific country and date
    """
    return await content_service.get_schedule(country, date)

@router.get("/people/search")
async def search_people(
    query: str,
    current_user: Optional[User] = Depends(get_current_user_optional)
) -> Any:
    """
    Search for people by name
    """
    return await content_service.search_people(query)

@router.get("/people/{person_id}")
async def get_person_details(
    person_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional)
) -> Any:
    """
    Get detailed information about a person
    """
    result = await content_service.get_person_details(person_id)
    if not result:
        raise HTTPException(status_code=404, detail="Person not found")
    return result

@router.get("/episode/{episode_id}")
async def get_episode_details(
    episode_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional)
) -> Any:
    """
    Get detailed information about an episode
    """
    result = await content_service.get_episode_details(episode_id)
    if not result:
        raise HTTPException(status_code=404, detail="Episode not found")
    return result

@router.get("/lookup")
async def lookup_show(
    imdb: Optional[str] = None,
    tvdb: Optional[str] = None,
    current_user: Optional[User] = Depends(get_current_user_optional)
) -> Any:
    """
    Look up a show by external ID (IMDb, TheTVDB)
    """
    if imdb:
        result = await content_service.get_show_by_external_id(imdb, "imdb")
    elif tvdb:
        result = await content_service.get_show_by_external_id(tvdb, "thetvdb")
    else:
        raise HTTPException(status_code=400, detail="No external ID provided")

    if not result:
        raise HTTPException(status_code=404, detail="Show not found")
    return result

@router.get("/updates/shows")
async def get_show_updates(
    since: Optional[int] = None,
    current_user: Optional[User] = Depends(get_current_user_optional)
) -> Any:
    """
    Get updates for shows since a specific timestamp
    """
    return await content_service.get_show_updates(since)

@router.get("/updates/people")
async def get_person_updates(
    since: Optional[int] = None,
    current_user: Optional[User] = Depends(get_current_user_optional)
) -> Any:
    """
    Get updates for people since a specific timestamp
    """
    return await content_service.get_person_updates(since)

@router.get("/schedule/web")
async def get_web_schedule(
    date: Optional[str] = None,
    country: str = "US",
    current_user: Optional[User] = Depends(get_current_user_optional)
) -> Any:
    """
    Get web/streaming schedule
    """
    return await content_service.get_web_schedule(date, country)

@router.get("/shows")
async def get_show_index(
    page: int = Query(1, ge=1),
    current_user: Optional[User] = Depends(get_current_user_optional)
) -> Any:
    """
    Get a paginated list of all shows
    """
    return await content_service.get_show_index(page)

@router.get("/people")
async def get_people_index(
    page: int = Query(1, ge=1),
    current_user: Optional[User] = Depends(get_current_user_optional)
) -> Any:
    """
    Get a paginated list of all people
    """
    return await content_service.get_people_index(page)