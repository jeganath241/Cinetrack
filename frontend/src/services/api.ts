import axios, { AxiosRequestConfig } from 'axios';
import {
  User,
  Token,
  Content,
  WatchlistItem,
  BucketListCreate,
  RecommendationCreate,
  CustomList,
  CustomListCreate,
  CustomListItem,
  CustomListItemCreate,
  WatchGoal,
  WatchGoalCreate,
  Achievement,
  UserAchievement,
  WatchHistory,
  WatchHistoryCreate,
  WeeklyStats,
  MonthlyStats,
  YearlyStats,
  GenreHeatmap
} from '../types/api';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if it exists
api.interceptors.request.use((config: AxiosRequestConfig) => {
  const token = localStorage.getItem('token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Add a response interceptor to handle token expiration
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const auth = {
  login: async (email: string, password: string): Promise<Token> => {
    const response = await api.post<Token>('/auth/login', { username: email, password });
    return response.data;
  },
  register: async (email: string, password: string): Promise<User> => {
    const response = await api.post<User>('/auth/register', { email, password });
    return response.data;
  },
};

export const content = {
  search: async (query: string, type?: string): Promise<Content[]> => {
    const response = await api.get<Content[]>('/content/search', {
      params: { query, type },
    });
    return response.data;
  },
  getDetails: async (imdbId: string): Promise<Content> => {
    const response = await api.get<Content>(`/content/${imdbId}`);
    return response.data;
  },
};

export const watchlist = {
  getAll: async (): Promise<WatchlistItem[]> => {
    const response = await api.get<WatchlistItem[]>('/watchlist');
    return response.data;
  },
  add: async (contentId: number, watchedEpisodes: number = 0, isCompleted: boolean = false): Promise<WatchlistItem> => {
    const response = await api.post<WatchlistItem>('/watchlist', {
      content_id: contentId,
      watched_episodes: watchedEpisodes,
      is_completed: isCompleted,
    });
    return response.data;
  },
  update: async (itemId: number, watchedEpisodes: number, isCompleted: boolean): Promise<WatchlistItem> => {
    const response = await api.put<WatchlistItem>(`/watchlist/${itemId}`, {
      content_id: itemId,
      watched_episodes: watchedEpisodes,
      is_completed: isCompleted,
    });
    return response.data;
  },
  remove: async (itemId: number): Promise<void> => {
    await api.delete(`/watchlist/${itemId}`);
  },
};

export const bucketList = {
  getAll: async () => {
    const response = await api.get('/bucketlist/');
    return response.data;
  },
  add: async (data: BucketListCreate) => {
    const response = await api.post('/bucketlist/', data);
    return response.data;
  },
  update: async (id: number, data: BucketListCreate) => {
    const response = await api.put(`/bucketlist/${id}`, data);
    return response.data;
  },
  remove: async (id: number) => {
    const response = await api.delete(`/bucketlist/${id}`);
    return response.data;
  },
};

export const recommendations = {
  getAll: async () => {
    const response = await api.get('/recommendations/');
    return response.data;
  },
  getPublic: async () => {
    const response = await api.get('/recommendations/public');
    return response.data;
  },
  create: async (data: RecommendationCreate) => {
    const response = await api.post('/recommendations/', data);
    return response.data;
  },
  update: async (id: number, data: RecommendationCreate) => {
    const response = await api.put(`/recommendations/${id}`, data);
    return response.data;
  },
  remove: async (id: number) => {
    const response = await api.delete(`/recommendations/${id}`);
    return response.data;
  },
};

export const customLists = {
  getAll: async (isPublic?: boolean) => {
    const response = await api.get<CustomList[]>('/lists/', {
      params: { is_public: isPublic },
    });
    return response.data;
  },
  getPublic: async () => {
    const response = await api.get<CustomList[]>('/lists/public');
    return response.data;
  },
  create: async (data: CustomListCreate) => {
    const response = await api.post<CustomList>('/lists/', data);
    return response.data;
  },
  getById: async (id: number) => {
    const response = await api.get<CustomList>(`/lists/${id}`);
    return response.data;
  },
  update: async (id: number, data: CustomListCreate) => {
    const response = await api.put<CustomList>(`/lists/${id}`, data);
    return response.data;
  },
  remove: async (id: number) => {
    const response = await api.delete(`/lists/${id}`);
    return response.data;
  },
  addItem: async (listId: number, data: CustomListItemCreate) => {
    const response = await api.post<CustomListItem>(`/lists/${listId}/items`, data);
    return response.data;
  },
  removeItem: async (listId: number, itemId: number) => {
    const response = await api.delete(`/lists/${listId}/items/${itemId}`);
    return response.data;
  },
};

export const goals = {
  getAll: async (isCompleted?: boolean) => {
    const response = await api.get<WatchGoal[]>('/goals/goals', {
      params: { is_completed: isCompleted },
    });
    return response.data;
  },
  create: async (data: WatchGoalCreate) => {
    const response = await api.post<WatchGoal>('/goals/goals', data);
    return response.data;
  },
  getById: async (id: number) => {
    const response = await api.get<WatchGoal>(`/goals/goals/${id}`);
    return response.data;
  },
  update: async (id: number, data: WatchGoalCreate) => {
    const response = await api.put<WatchGoal>(`/goals/goals/${id}`, data);
    return response.data;
  },
  remove: async (id: number) => {
    const response = await api.delete(`/goals/goals/${id}`);
    return response.data;
  },
  getAllAchievements: async () => {
    const response = await api.get<Achievement[]>('/goals/achievements');
    return response.data;
  },
  getUserAchievements: async () => {
    const response = await api.get<UserAchievement[]>('/goals/achievements/user');
    return response.data;
  },
  checkAchievements: async () => {
    const response = await api.post<UserAchievement[]>('/goals/achievements/check');
    return response.data;
  },
};

export const analytics = {
  addWatchHistory: async (data: WatchHistoryCreate) => {
    const response = await api.post<WatchHistory>('/analytics/history', data);
    return response.data;
  },
  getWatchHistory: async (startDate?: string, endDate?: string, contentType?: string) => {
    const response = await api.get<WatchHistory[]>('/analytics/history', {
      params: { start_date: startDate, end_date: endDate, content_type: contentType },
    });
    return response.data;
  },
  getWeeklyStats: async () => {
    const response = await api.get<WeeklyStats>('/analytics/stats/weekly');
    return response.data;
  },
  getMonthlyStats: async () => {
    const response = await api.get<MonthlyStats>('/analytics/stats/monthly');
    return response.data;
  },
  getYearlyStats: async () => {
    const response = await api.get<YearlyStats>('/analytics/stats/yearly');
    return response.data;
  },
  getGenreHeatmap: async () => {
    const response = await api.get<GenreHeatmap>('/analytics/stats/heatmap');
    return response.data;
  },
};

export default api; 