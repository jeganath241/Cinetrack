from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, or_, and_
from app.db.session import get_db
from app.models.models import User, Content, BucketList
from app.schemas.schemas import BucketList as BucketListSchema, BucketListCreate
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

@router.get("/", response_model=List[BucketListSchema])
async def get_bucket_list(
    current_user: User = Depends(get_current_user),
    content_type: Optional[str] = None,
    genre: Optional[str] = None,
    language: Optional[str] = None,
    is_watched: Optional[bool] = None,
    sort_by: Optional[str] = "created_at",
    session: Session = Depends(get_db)
) -> Any:
    # Build the base query
    base_query = select(BucketList).where(BucketList.user_id == current_user.id)
    
    # Add filters
    if content_type:
        base_query = base_query.join(Content).where(Content.content_type == content_type)
    if genre:
        base_query = base_query.join(Content).where(Content.genres.ilike(f"%{genre}%"))
    if language:
        base_query = base_query.join(Content).where(Content.language == language)
    if is_watched is not None:
        base_query = base_query.where(BucketList.is_watched == is_watched)
    
    # Add sorting
    if sort_by == "created_at":
        base_query = base_query.order_by(BucketList.created_at.desc())
    elif sort_by == "imdb_rating":
        base_query = base_query.join(Content).order_by(Content.imdb_rating.desc())
    
    # Execute the query
    results = session.exec(base_query).all()
    return results

@router.post("/", response_model=BucketListSchema)
async def add_to_bucket_list(
    bucket_list_item: BucketListCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
) -> Any:
    # Check if content exists
    content = session.exec(select(Content).where(Content.id == bucket_list_item.content_id)).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    # Check if already in bucket list
    existing_item = session.exec(
        select(BucketList)
        .where(BucketList.user_id == current_user.id)
        .where(BucketList.content_id == bucket_list_item.content_id)
    ).first()
    if existing_item:
        raise HTTPException(status_code=400, detail="Content already in bucket list")
    
    db_item = BucketList(
        user_id=current_user.id,
        content_id=bucket_list_item.content_id,
        is_watched=bucket_list_item.is_watched,
        watched_at=bucket_list_item.watched_at
    )
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

@router.put("/{item_id}", response_model=BucketListSchema)
async def update_bucket_list_item(
    item_id: int,
    bucket_list_item: BucketListCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
) -> Any:
    db_item = session.exec(
        select(BucketList)
        .where(BucketList.id == item_id)
        .where(BucketList.user_id == current_user.id)
    ).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Bucket list item not found")
    
    db_item.is_watched = bucket_list_item.is_watched
    db_item.watched_at = bucket_list_item.watched_at
    
    session.commit()
    session.refresh(db_item)
    return db_item

@router.delete("/{item_id}")
async def remove_from_bucket_list(
    item_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
) -> Any:
    db_item = session.exec(
        select(BucketList)
        .where(BucketList.id == item_id)
        .where(BucketList.user_id == current_user.id)
    ).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Bucket list item not found")
    
    session.delete(db_item)
    session.commit()
    return {"message": "Item removed from bucket list"} 