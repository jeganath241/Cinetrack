from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, or_, and_
from app.db.session import get_db
from app.models.models import User, WatchGoal, Achievement, UserAchievement
from app.schemas.schemas import (
    WatchGoal as WatchGoalSchema,
    WatchGoalCreate,
    Achievement as AchievementSchema,
    UserAchievement as UserAchievementSchema
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

@router.get("/goals", response_model=List[WatchGoalSchema])
async def get_watch_goals(
    current_user: User = Depends(get_current_user),
    is_completed: Optional[bool] = None,
    session: Session = Depends(get_db)
) -> Any:
    query = select(WatchGoal).where(WatchGoal.user_id == current_user.id)
    if is_completed is not None:
        query = query.where(WatchGoal.is_completed == is_completed)
    results = session.exec(query).all()
    return results

@router.post("/goals", response_model=WatchGoalSchema)
async def create_watch_goal(
    goal: WatchGoalCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
) -> Any:
    db_goal = WatchGoal(
        **goal.dict(),
        user_id=current_user.id
    )
    session.add(db_goal)
    session.commit()
    session.refresh(db_goal)
    return db_goal

@router.get("/goals/{goal_id}", response_model=WatchGoalSchema)
async def get_watch_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
) -> Any:
    goal = session.exec(
        select(WatchGoal)
        .where(WatchGoal.id == goal_id)
        .where(WatchGoal.user_id == current_user.id)
    ).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal

@router.put("/goals/{goal_id}", response_model=WatchGoalSchema)
async def update_watch_goal(
    goal_id: int,
    goal: WatchGoalCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
) -> Any:
    db_goal = session.exec(
        select(WatchGoal)
        .where(WatchGoal.id == goal_id)
        .where(WatchGoal.user_id == current_user.id)
    ).first()
    if not db_goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    for key, value in goal.dict().items():
        setattr(db_goal, key, value)
    
    session.commit()
    session.refresh(db_goal)
    return db_goal

@router.delete("/goals/{goal_id}")
async def delete_watch_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
) -> Any:
    db_goal = session.exec(
        select(WatchGoal)
        .where(WatchGoal.id == goal_id)
        .where(WatchGoal.user_id == current_user.id)
    ).first()
    if not db_goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    session.delete(db_goal)
    session.commit()
    return {"message": "Goal deleted"}

@router.get("/achievements", response_model=List[AchievementSchema])
async def get_achievements(
    session: Session = Depends(get_db)
) -> Any:
    results = session.exec(select(Achievement)).all()
    return results

@router.get("/achievements/user", response_model=List[UserAchievementSchema])
async def get_user_achievements(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
) -> Any:
    results = session.exec(
        select(UserAchievement)
        .where(UserAchievement.user_id == current_user.id)
    ).all()
    return results

@router.post("/achievements/check", response_model=List[UserAchievementSchema])
async def check_achievements(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_db)
) -> Any:
    # Get all achievements
    achievements = session.exec(select(Achievement)).all()
    # Get user's current achievements
    user_achievements = session.exec(
        select(UserAchievement)
        .where(UserAchievement.user_id == current_user.id)
    ).all()
    user_achievement_ids = {ua.achievement_id for ua in user_achievements}
    
    # Get user's watch history stats
    watch_history = session.exec(
        select(User.watch_history)
        .where(User.id == current_user.id)
    ).first()
    
    new_achievements = []
    for achievement in achievements:
        if achievement.id not in user_achievement_ids:
            # Check if user meets achievement criteria
            if achievement.achievement_type == "movies":
                count = len([wh for wh in watch_history if wh.content.content_type == "movie"])
            elif achievement.achievement_type == "series":
                count = len([wh for wh in watch_history if wh.content.content_type == "series"])
            elif achievement.achievement_type == "hours":
                count = sum(wh.duration_minutes for wh in watch_history) / 60
            else:
                continue
            
            if count >= achievement.required_count:
                user_achievement = UserAchievement(
                    user_id=current_user.id,
                    achievement_id=achievement.id,
                    earned_at=datetime.utcnow()
                )
                session.add(user_achievement)
                new_achievements.append(user_achievement)
    
    if new_achievements:
        session.commit()
        for achievement in new_achievements:
            session.refresh(achievement)
    
    return new_achievements 