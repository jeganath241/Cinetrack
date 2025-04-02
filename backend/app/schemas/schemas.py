from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import EmailStr, BaseModel
from sqlmodel import SQLModel, Field
from app.models.models import ContentType

class UserBase(SQLModel):
    username: str
    email: EmailStr
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    ratings: List["Rating"] = []
    reviews: List["Review"] = []
    bucket_list: List["BucketList"] = []
    recommendations: List["Recommendation"] = []
    custom_lists: List["CustomList"] = []
    watch_goals: List["WatchGoal"] = []
    achievements: List["UserAchievement"] = []
    watch_history: List["WatchHistory"] = []

    class Config:
        from_attributes = True

class Token(SQLModel):
    access_token: str
    token_type: str

class TokenData(SQLModel):
    email: Optional[str] = None

class ContentBase(SQLModel):
    title: str
    content_type: ContentType
    imdb_id: str
    imdb_rating: Optional[float] = None
    total_episodes: Optional[int] = None
    release_date: Optional[datetime] = None
    poster_url: Optional[str] = None
    description: Optional[str] = None
    genres: Optional[str] = None
    language: Optional[str] = None
    runtime_minutes: Optional[int] = None
    episode_runtime_minutes: Optional[int] = None

class ContentCreate(ContentBase):
    pass

class Content(ContentBase):
    id: int
    created_at: datetime
    ratings: List["Rating"] = []
    reviews: List["Review"] = []
    bucket_list: List["BucketList"] = []
    recommendations: List["Recommendation"] = []
    custom_list_items: List["CustomListItem"] = []
    watch_history: List["WatchHistory"] = []

    class Config:
        from_attributes = True

class WatchlistBase(SQLModel):
    watched_episodes: int = 0
    is_completed: bool = False
    created_at: datetime
    updated_at: datetime

class WatchlistCreate(WatchlistBase):
    content_id: int

class Watchlist(WatchlistBase):
    id: int
    user_id: int
    content_id: int
    content: Content

    class Config:
        from_attributes = True

class RatingBase(SQLModel):
    rating: int
    created_at: datetime
    updated_at: datetime

class RatingCreate(RatingBase):
    content_id: int

class Rating(RatingBase):
    id: int
    user_id: int
    content_id: int
    content: Content
    user: User

    class Config:
        from_attributes = True

class ReviewBase(SQLModel):
    description: str
    is_private: bool = False
    created_at: datetime
    updated_at: datetime

class ReviewCreate(ReviewBase):
    content_id: int

class Review(ReviewBase):
    id: int
    user_id: int
    content_id: int
    content: Content
    user: User

    class Config:
        from_attributes = True

class BucketListBase(SQLModel):
    created_at: datetime
    is_watched: bool = False
    watched_at: Optional[datetime] = None

class BucketListCreate(BucketListBase):
    content_id: int

class BucketList(BucketListBase):
    id: int
    user_id: int
    content_id: int
    content: Content
    user: User

    class Config:
        from_attributes = True

class RecommendationBase(SQLModel):
    created_at: datetime
    is_public: bool = True
    note: Optional[str] = None

class RecommendationCreate(RecommendationBase):
    content_id: int

class Recommendation(RecommendationBase):
    id: int
    user_id: int
    content_id: int
    content: Content
    user: User

    class Config:
        from_attributes = True

class CustomListBase(SQLModel):
    name: str
    description: Optional[str] = None
    is_public: bool = False
    created_at: datetime
    updated_at: datetime

class CustomListCreate(CustomListBase):
    pass

class CustomList(CustomListBase):
    id: int
    user_id: int
    items: List["CustomListItem"] = []
    user: User

    class Config:
        from_attributes = True

class CustomListItemBase(SQLModel):
    added_at: datetime
    note: Optional[str] = None

class CustomListItemCreate(CustomListItemBase):
    list_id: int
    content_id: int

class CustomListItem(CustomListItemBase):
    id: int
    list_id: int
    content_id: int
    list: CustomList
    content: Content

    class Config:
        from_attributes = True

class WatchGoalBase(SQLModel):
    name: str
    target_count: int
    target_type: str
    start_date: datetime
    end_date: datetime
    is_completed: bool = False
    created_at: datetime
    updated_at: datetime

class WatchGoalCreate(WatchGoalBase):
    pass

class WatchGoal(WatchGoalBase):
    id: int
    user_id: int
    user: User

    class Config:
        from_attributes = True

class AchievementBase(SQLModel):
    name: str
    description: str
    icon_url: Optional[str] = None
    required_count: int
    achievement_type: str

class Achievement(AchievementBase):
    id: int
    user_achievements: List["UserAchievement"] = []

    class Config:
        from_attributes = True

class UserAchievementBase(SQLModel):
    earned_at: datetime

class UserAchievement(UserAchievementBase):
    id: int
    user_id: int
    achievement_id: int
    user: User
    achievement: Achievement

    class Config:
        from_attributes = True

class WatchHistoryBase(SQLModel):
    watched_at: datetime
    duration_minutes: int
    platform: Optional[str] = None
    episode_number: Optional[int] = None
    season_number: Optional[int] = None

class WatchHistoryCreate(WatchHistoryBase):
    content_id: int

class WatchHistory(WatchHistoryBase):
    id: int
    user_id: int
    content_id: int
    user: User
    content: Content

    class Config:
        from_attributes = True

class ContentResponse(BaseModel):
    id: int
    title: str
    overview: Optional[str] = None
    poster_url: Optional[str] = None
    backdrop_url: Optional[str] = None
    release_date: Optional[str] = None
    rating: Optional[float] = None
    genres: List[str] = []
    status: Optional[str] = None
    runtime: Optional[int] = None
    type: str = "tv"
    network: Optional[str] = None
    schedule: Optional[Dict[str, Any]] = None
    web_channel: Optional[str] = None
    externals: Optional[Dict[str, Any]] = None
    updated: Optional[str] = None

class CastMember(BaseModel):
    id: int
    name: str
    character: Optional[str] = None
    profile_url: Optional[str] = None

class CrewMember(BaseModel):
    id: int
    name: str
    department: str
    job: str
    profile_url: Optional[str] = None

class CreditsResponse(BaseModel):
    cast: List[CastMember]
    crew: List[CrewMember]

class SearchResponse(BaseModel):
    results: List[ContentResponse]
    page: int
    total_pages: int
    total_results: int

class SimilarContentResponse(BaseModel):
    results: List[ContentResponse]
    page: int
    total_pages: int
    total_results: int

class Genre(BaseModel):
    id: int
    name: str

class AnalyticsBase(SQLModel):
    total_watch_time: int = 0  # in minutes
    total_content_watched: int = 0
    favorite_genres: str = "[]"  # Store as JSON string
    favorite_actors: str = "[]"  # Store as JSON string
    favorite_directors: str = "[]"  # Store as JSON string
    average_rating: float = 0.0

class AnalyticsCreate(AnalyticsBase):
    user_id: int

class AnalyticsResponse(AnalyticsBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 