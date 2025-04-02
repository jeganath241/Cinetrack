from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.db.session import get_db
from app.models.models import User, Content, Watchlist
from app.schemas.schemas import Watchlist as WatchlistSchema, WatchlistCreate
from app.api.v1.endpoints.auth import oauth2_scheme
from app.core import security

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

@router.get("/", response_model=List[WatchlistSchema])
async def get_watchlist(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
) -> Any:
    return session.exec(select(Watchlist).where(Watchlist.user_id == current_user.id)).all()

@router.post("/", response_model=WatchlistSchema)
async def add_to_watchlist(
    watchlist_item: WatchlistCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
) -> Any:
    # Check if content exists
    content = session.exec(select(Content).where(Content.id == watchlist_item.content_id)).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    # Check if already in watchlist
    existing_item = session.exec(
        select(Watchlist)
        .where(Watchlist.user_id == current_user.id)
        .where(Watchlist.content_id == watchlist_item.content_id)
    ).first()
    if existing_item:
        raise HTTPException(status_code=400, detail="Content already in watchlist")
    
    db_item = Watchlist(
        user_id=current_user.id,
        content_id=watchlist_item.content_id,
        watched_episodes=watchlist_item.watched_episodes,
        is_completed=watchlist_item.is_completed
    )
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

@router.put("/{item_id}", response_model=WatchlistSchema)
async def update_watchlist_item(
    item_id: int,
    watchlist_item: WatchlistCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
) -> Any:
    db_item = session.exec(
        select(Watchlist)
        .where(Watchlist.id == item_id)
        .where(Watchlist.user_id == current_user.id)
    ).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Watchlist item not found")
    
    for key, value in watchlist_item.dict().items():
        setattr(db_item, key, value)
    
    session.commit()
    session.refresh(db_item)
    return db_item

@router.delete("/{item_id}")
async def remove_from_watchlist(
    item_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
) -> Any:
    db_item = session.exec(
        select(Watchlist)
        .where(Watchlist.id == item_id)
        .where(Watchlist.user_id == current_user.id)
    ).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Watchlist item not found")
    
    session.delete(db_item)
    session.commit()
    return {"message": "Item removed from watchlist"} 