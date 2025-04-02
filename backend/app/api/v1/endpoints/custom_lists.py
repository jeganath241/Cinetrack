from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, or_, and_
from app.db.session import get_db
from app.models.models import User, Content, CustomList, CustomListItem
from app.schemas.schemas import (
    CustomList as CustomListSchema,
    CustomListCreate,
    CustomListItem as CustomListItemSchema,
    CustomListItemCreate
)
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

@router.get("/", response_model=List[CustomListSchema])
async def get_custom_lists(
    current_user: User = Depends(get_current_user),
    is_public: Optional[bool] = None,
    session: Session = Depends(get_db)
) -> Any:
    query = select(CustomList).where(CustomList.user_id == current_user.id)
    if is_public is not None:
        query = query.where(CustomList.is_public == is_public)
    results = session.exec(query).all()
    return results

@router.get("/public", response_model=List[CustomListSchema])
async def get_public_lists(
    session: Session = Depends(get_db)
) -> Any:
    results = session.exec(select(CustomList).where(CustomList.is_public == True)).all()
    return results

@router.post("/", response_model=CustomListSchema)
async def create_custom_list(
    custom_list: CustomListCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
) -> Any:
    db_list = CustomList(
        **custom_list.dict(),
        user_id=current_user.id
    )
    session.add(db_list)
    session.commit()
    session.refresh(db_list)
    return db_list

@router.get("/{list_id}", response_model=CustomListSchema)
async def get_custom_list(
    list_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
) -> Any:
    list = session.exec(
        select(CustomList)
        .where(CustomList.id == list_id)
        .where(
            or_(
                CustomList.user_id == current_user.id,
                CustomList.is_public == True
            )
        )
    ).first()
    if not list:
        raise HTTPException(status_code=404, detail="List not found")
    return list

@router.put("/{list_id}", response_model=CustomListSchema)
async def update_custom_list(
    list_id: int,
    custom_list: CustomListCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
) -> Any:
    db_list = session.exec(
        select(CustomList)
        .where(CustomList.id == list_id)
        .where(CustomList.user_id == current_user.id)
    ).first()
    if not db_list:
        raise HTTPException(status_code=404, detail="List not found")
    
    for key, value in custom_list.dict().items():
        setattr(db_list, key, value)
    
    session.commit()
    session.refresh(db_list)
    return db_list

@router.delete("/{list_id}")
async def delete_custom_list(
    list_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
) -> Any:
    db_list = session.exec(
        select(CustomList)
        .where(CustomList.id == list_id)
        .where(CustomList.user_id == current_user.id)
    ).first()
    if not db_list:
        raise HTTPException(status_code=404, detail="List not found")
    
    session.delete(db_list)
    session.commit()
    return {"message": "List deleted"}

@router.post("/{list_id}/items", response_model=CustomListItemSchema)
async def add_to_custom_list(
    list_id: int,
    item: CustomListItemCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
) -> Any:
    # Check if list exists and belongs to user
    custom_list = session.exec(
        select(CustomList)
        .where(CustomList.id == list_id)
        .where(CustomList.user_id == current_user.id)
    ).first()
    if not custom_list:
        raise HTTPException(status_code=404, detail="List not found")
    
    # Check if content exists
    content = session.exec(select(Content).where(Content.id == item.content_id)).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    # Check if item already in list
    existing_item = session.exec(
        select(CustomListItem)
        .where(CustomListItem.list_id == list_id)
        .where(CustomListItem.content_id == item.content_id)
    ).first()
    if existing_item:
        raise HTTPException(status_code=400, detail="Content already in list")
    
    db_item = CustomListItem(
        **item.dict(),
        list_id=list_id
    )
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item

@router.delete("/{list_id}/items/{item_id}")
async def remove_from_custom_list(
    list_id: int,
    item_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
) -> Any:
    # Check if list exists and belongs to user
    custom_list = session.exec(
        select(CustomList)
        .where(CustomList.id == list_id)
        .where(CustomList.user_id == current_user.id)
    ).first()
    if not custom_list:
        raise HTTPException(status_code=404, detail="List not found")
    
    # Check if item exists and belongs to list
    item = session.exec(
        select(CustomListItem)
        .where(CustomListItem.id == item_id)
        .where(CustomListItem.list_id == list_id)
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    session.delete(item)
    session.commit()
    return {"message": "Item removed from list"} 