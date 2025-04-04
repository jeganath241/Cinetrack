import axios, { InternalAxiosRequestConfig } from 'axios';
import {
  User,
  Token,
  Content,
  WatchlistItem,
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
  GenreHeatmap,
  RecommendationCreate
} from '../types/api';

// Declare the env property on ImportMeta
declare global {
  interface ImportMeta {
    env: {
      VITE_API_URL: string;
    };
  }
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Enable sending cookies with requests
});

// Add token to requests if it exists
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem('token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Add a response interceptor to handle token expiration and errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Only remove token and trigger event if it's not an auth endpoint
      const isAuthEndpoint = error.config.url?.includes('/auth/');
      if (!isAuthEndpoint) {
        localStorage.removeItem('token');
        window.dispatchEvent(new CustomEvent('auth:logout'));
      }
    }
    return Promise.reject(error);
  }
);

// Listen for auth events
window.addEventListener('auth:logout', () => {
  // Redirect to login page
  window.location.href = '/login';
});

export const auth = {
  login: async (email: string, password: string): Promise<Token> => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    const response = await api.post<Token>('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },
  register: async (username: string, email: string, password: string): Promise<User> => {
    try {
      console.log('Registering user:', { username, email });
      const response = await api.post<User>('/auth/register', { username, email, password });
      console.log('Registration response:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('Registration error:', error.response?.data || error.message);
      throw error;
    }
  },
  getCurrentUser: async (): Promise<User> => {
    const response = await api.get<User>('/auth/me');
    return response.data;
  },
};

export const content = {
  search: async (query: string, type?: string, language?: string) => {
    const response = await api.get('/content/search', {
      params: { query, type, language },
    });
    return response.data;
  },
  getShowDetails: async (showId: number) => {
    const response = await api.get(`/content/show/${showId}`);
    return response.data;
  },
  getEpisodeDetails: async (episodeId: number) => {
    const response = await api.get(`/content/episode/${episodeId}`);
    return response.data;
  },
  lookupShow: async (params: { imdb?: string; tvdb?: string }) => {
    const response = await api.get('/content/lookup', { params });
    return response.data;
  },
  getSchedule: async (country: string = 'US', date?: string) => {
    const response = await api.get('/content/schedule', {
      params: { country, date },
    });
    return response.data;
  },
  getWebSchedule: async (country: string = 'US', date?: string) => {
    const response = await api.get('/content/schedule/web', {
      params: { country, date },
    });
    return response.data;
  },
  searchPeople: async (query: string) => {
    const response = await api.get('/content/people/search', {
      params: { query },
    });
    return response.data;
  },
  getPersonDetails: async (personId: number) => {
    const response = await api.get(`/content/people/${personId}`);
    return response.data;
  },
  getShowUpdates: async (since?: number) => {
    const response = await api.get('/content/updates/shows', {
      params: { since },
    });
    return response.data;
  },
  getPersonUpdates: async (since?: number) => {
    const response = await api.get('/content/updates/people', {
      params: { since },
    });
    return response.data;
  },
  getShowIndex: async (page: number = 1) => {
    const response = await api.get('/content/shows', {
      params: { page },
    });
    return response.data;
  },
  getPeopleIndex: async (page: number = 1) => {
    const response = await api.get('/content/people', {
      params: { page },
    });
    return response.data;
  },
};

export const watchlist = {
  getAll: async (): Promise<WatchlistItem[]> => {
    const response = await api.get<WatchlistItem[]>('/watchlist');
    return response.data;
  },
  add: async (contentId: number): Promise<WatchlistItem> => {
    const response = await api.post('/watchlist', { content_id: contentId });
    return response.data;
  },
  update: async (itemId: number, watchedEpisodes: number, isCompleted: boolean): Promise<WatchlistItem> => {
    const response = await api.put(`/watchlist/${itemId}`, { watched_episodes: watchedEpisodes, is_completed: isCompleted });
    return response.data;
  },
  remove: async (itemId: number): Promise<void> => {
    await api.delete(`/watchlist/${itemId}`);
  },
};

export const bucketList = {
  getAll: async () => {
    const response = await api.get('/bucketlist');
    return response.data;
  },
  add: async (contentId: number) => {
    const response = await api.post('/bucketlist', { content_id: contentId });
    return response.data;
  },
  update: async (id: number, data: any) => {
    const response = await api.put(`/bucketlist/${id}`, data);
    return response.data;
  },
  remove: async (id: number) => {
    await api.delete(`/bucketlist/${id}`);
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