from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from enum import Enum
import json

class ContentType(str, Enum):
    MOVIE = "movie"
    SERIES = "series"
    ANIME = "anime"

class UserBase(SQLModel):
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    full_name: Optional[str] = None
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    watchlist: List["Watchlist"] = Relationship(back_populates="user")
    ratings: List["Rating"] = Relationship(back_populates="user")
    reviews: List["Review"] = Relationship(back_populates="user")
    bucket_list: List["BucketList"] = Relationship(back_populates="user")
    recommendations: List["Recommendation"] = Relationship(back_populates="user")
    custom_lists: List["CustomList"] = Relationship(back_populates="user")
    watch_goals: List["WatchGoal"] = Relationship(back_populates="user")
    achievements: List["UserAchievement"] = Relationship(back_populates="user")
    watch_history: List["WatchHistory"] = Relationship(back_populates="user")
    analytics: List["Analytics"] = Relationship(back_populates="user")

class ContentBase(SQLModel):
    title: str
    content_type: ContentType
    imdb_id: str = Field(unique=True, index=True)
    imdb_rating: Optional[float] = None
    total_episodes: Optional[int] = None
    release_date: Optional[datetime] = None
    poster_url: Optional[str] = None
    description: Optional[str] = None
    genres: Optional[str] = None  # Store as comma-separated string
    language: Optional[str] = None
    runtime_minutes: Optional[int] = None  # For movies
    episode_runtime_minutes: Optional[int] = None  # For series/anime

class Content(ContentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    watchlist: List["Watchlist"] = Relationship(back_populates="content")
    ratings: List["Rating"] = Relationship(back_populates="content")
    reviews: List["Review"] = Relationship(back_populates="content")
    bucket_list: List["BucketList"] = Relationship(back_populates="content")
    recommendations: List["Recommendation"] = Relationship(back_populates="content")
    custom_list_items: List["CustomListItem"] = Relationship(back_populates="content")
    watch_history: List["WatchHistory"] = Relationship(back_populates="content")

class WatchlistBase(SQLModel):
    watched_episodes: int = Field(default=0)
    is_completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Watchlist(WatchlistBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    content_id: int = Field(foreign_key="content.id")
    user: User = Relationship(back_populates="watchlist")
    content: Content = Relationship(back_populates="watchlist")

class RatingBase(SQLModel):
    rating: int = Field(ge=1, le=10)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Rating(RatingBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    content_id: int = Field(foreign_key="content.id")
    user: User = Relationship(back_populates="ratings")
    content: Content = Relationship(back_populates="ratings")

class ReviewBase(SQLModel):
    description: str
    is_private: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Review(ReviewBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    content_id: int = Field(foreign_key="content.id")
    user: User = Relationship(back_populates="reviews")
    content: Content = Relationship(back_populates="reviews")

class BucketListBase(SQLModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_watched: bool = Field(default=False)
    watched_at: Optional[datetime] = None

class BucketList(BucketListBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    content_id: int = Field(foreign_key="content.id")
    user: User = Relationship(back_populates="bucket_list")
    content: Content = Relationship(back_populates="bucket_list")

class RecommendationBase(SQLModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_public: bool = Field(default=True)
    note: Optional[str] = None

class Recommendation(RecommendationBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    content_id: int = Field(foreign_key="content.id")
    user: User = Relationship(back_populates="recommendations")
    content: Content = Relationship(back_populates="recommendations")

class CustomListBase(SQLModel):
    name: str
    description: Optional[str] = None
    is_public: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CustomList(CustomListBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="custom_lists")
    items: List["CustomListItem"] = Relationship(back_populates="list")

class CustomListItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    list_id: int = Field(foreign_key="customlist.id")
    content_id: int = Field(foreign_key="content.id")
    added_at: datetime = Field(default_factory=datetime.utcnow)
    note: Optional[str] = None
    list: CustomList = Relationship(back_populates="items")
    content: Content = Relationship(back_populates="custom_list_items")

class WatchGoalBase(SQLModel):
    name: str
    target_count: int
    target_type: str  # "movies", "series", "hours", etc.
    start_date: datetime
    end_date: datetime
    is_completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class WatchGoal(WatchGoalBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="watch_goals")

class AchievementBase(SQLModel):
    name: str
    description: str
    icon_url: Optional[str] = None
    required_count: int
    achievement_type: str  # "movies", "series", "hours", etc.

class Achievement(AchievementBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_achievements: List["UserAchievement"] = Relationship(back_populates="achievement")

class UserAchievement(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    achievement_id: int = Field(foreign_key="achievement.id")
    earned_at: datetime = Field(default_factory=datetime.utcnow)
    user: User = Relationship(back_populates="achievements")
    achievement: Achievement = Relationship(back_populates="user_achievements")

class WatchHistoryBase(SQLModel):
    watched_at: datetime
    duration_minutes: int
    platform: Optional[str] = None  # "netflix", "crunchyroll", etc.
    episode_number: Optional[int] = None
    season_number: Optional[int] = None

class WatchHistory(WatchHistoryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    content_id: int = Field(foreign_key="content.id")
    user: User = Relationship(back_populates="watch_history")
    content: Content = Relationship(back_populates="watch_history")

class Analytics(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    user: User = Relationship(back_populates="analytics")
    total_watch_time: int = Field(default=0)  # in minutes
    total_content_watched: int = Field(default=0)
    favorite_genres: str = Field(default="[]")  # Store as JSON string
    favorite_actors: str = Field(default="[]")  # Store as JSON string
    favorite_directors: str = Field(default="[]")  # Store as JSON string
    average_rating: float = Field(default=0.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def get_favorite_genres(self) -> List[str]:
        return json.loads(self.favorite_genres)

    def set_favorite_genres(self, genres: List[str]):
        self.favorite_genres = json.dumps(genres)

    def get_favorite_actors(self) -> List[str]:
        return json.loads(self.favorite_actors)

    def set_favorite_actors(self, actors: List[str]):
        self.favorite_actors = json.dumps(actors)

    def get_favorite_directors(self) -> List[str]:
        return json.loads(self.favorite_directors)

    def set_favorite_directors(self, directors: List[str]):
        self.favorite_directors = json.dumps(directors) 