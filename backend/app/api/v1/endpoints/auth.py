from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session, select
from app.core import security
from app.core.config import settings
from app.db.session import get_db
from app.models.models import User
from app.schemas.schemas import User as UserSchema, UserCreate, Token
import jwt

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception
    
    user = session.exec(select(User).where(User.email == email)).first()
    if user is None:
        raise credentials_exception
    return user

@router.get("/me", response_model=UserSchema)
async def read_users_me(current_user: User = Depends(get_current_user)) -> Any:
    return current_user

@router.post("/register", response_model=UserSchema)
def register(user: UserCreate, session: Session = Depends(get_db)) -> Any:
    try:
        # Check if email is already registered
        db_user = session.exec(select(User).where(User.email == user.email)).first()
        if db_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
        
        # Check if username is already taken
        db_user = session.exec(select(User).where(User.username == user.username)).first()
        if db_user:
            raise HTTPException(
                status_code=400,
                detail="Username already taken"
            )
        
        hashed_password = security.get_password_hash(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password
        )
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.post("/login", response_model=Token)
def login(
    session: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    user = session.exec(select(User).where(User.email == form_data.username)).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user.email,
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"} 