export interface User {
  id: number;
  email: string;
  is_active: boolean;
  created_at: string;
  bucket_list: BucketList[];
  recommendations: Recommendation[];
  custom_lists: CustomList[];
  watch_goals: WatchGoal[];
  achievements: UserAchievement[];
  watch_history: WatchHistory[];
}

export interface Token {
  access_token: string;
  token_type: string;
}

export type ContentType = 'movie' | 'series' | 'anime';

export interface Content {
  id: number;
  imdb_id: string;
  title: string;
  type: ContentType;
  poster_url: string;
  year: number;
  description: string;
  total_episodes?: number;
  created_at: string;
  bucket_list: BucketList[];
  recommendations: Recommendation[];
  custom_list_items: CustomListItem[];
  watch_history: WatchHistory[];
  runtime_minutes?: number;
  episode_runtime_minutes?: number;
}

export interface WatchlistItem {
  id: number;
  user_id: number;
  content_id: number;
  watched_episodes: number;
  is_completed: boolean;
  created_at: string;
  updated_at: string;
  content: Content;
}

export interface BucketList {
  id: number;
  user_id: number;
  content_id: number;
  created_at: string;
  is_watched: boolean;
  watched_at: string | null;
  user: User;
  content: Content;
}

export interface BucketListCreate {
  content_id: number;
  is_watched: boolean;
  watched_at: string | null;
}

export interface Recommendation {
  id: number;
  user_id: number;
  content_id: number;
  created_at: string;
  is_public: boolean;
  note: string | null;
  user: User;
  content: Content;
}

export interface RecommendationCreate {
  content_id: number;
  is_public: boolean;
  note: string | null;
}

export interface TokenData {
  email: string | null;
}

export interface CustomList {
  id: number;
  user_id: number;
  name: string;
  description: string | null;
  is_public: boolean;
  created_at: string;
  updated_at: string;
  items: CustomListItem[];
  user: User;
}

export interface CustomListCreate {
  name: string;
  description: string | null;
  is_public: boolean;
}

export interface CustomListItem {
  id: number;
  list_id: number;
  content_id: number;
  added_at: string;
  note: string | null;
  list: CustomList;
  content: Content;
}

export interface CustomListItemCreate {
  list_id: number;
  content_id: number;
  note: string | null;
}

export interface WatchGoal {
  id: number;
  user_id: number;
  name: string;
  target_count: number;
  target_type: string;
  start_date: string;
  end_date: string;
  is_completed: boolean;
  created_at: string;
  updated_at: string;
  user: User;
}

export interface WatchGoalCreate {
  name: string;
  target_count: number;
  target_type: string;
  start_date: string;
  end_date: string;
}

export interface Achievement {
  id: number;
  name: string;
  description: string;
  icon_url: string | null;
  required_count: number;
  achievement_type: string;
  user_achievements: UserAchievement[];
}

export interface UserAchievement {
  id: number;
  user_id: number;
  achievement_id: number;
  earned_at: string;
  user: User;
  achievement: Achievement;
}

export interface WatchHistory {
  id: number;
  user_id: number;
  content_id: number;
  watched_at: string;
  duration_minutes: number;
  platform: string | null;
  episode_number: number | null;
  season_number: number | null;
  user: User;
  content: Content;
}

export interface WatchHistoryCreate {
  content_id: number;
  duration_minutes: number;
  platform: string | null;
  episode_number: number | null;
  season_number: number | null;
}

export interface WeeklyStats {
  total_minutes: number;
  total_movies: number;
  total_series: number;
  total_anime: number;
  genre_distribution: Record<string, number>;
}

export interface MonthlyStats {
  total_minutes: number;
  total_movies: number;
  total_series: number;
  total_anime: number;
  genre_distribution: Record<string, number>;
}

export interface YearlyStats {
  total_minutes: number;
  total_movies: number;
  total_series: number;
  total_anime: number;
  genre_distribution: Record<string, number>;
  top_movies: Array<{
    title: string;
    rating: number;
    watched_at: string;
  }>;
}

export interface GenreHeatmap {
  [genre: string]: {
    count: number;
    total_minutes: number;
    movies: number;
    series: number;
    anime: number;
  };
} 