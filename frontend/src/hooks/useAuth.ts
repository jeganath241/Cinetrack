import { useState, useEffect } from 'react';
import { api } from '../services/api';

interface AuthState {
  isAuthenticated: boolean;
  user: any | null;
}

export const useAuth = () => {
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    user: null,
  });

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      // Verify token and get user data
      api.get('/auth/me')
        .then(response => {
          setAuthState({
            isAuthenticated: true,
            user: response.data,
          });
        })
        .catch(() => {
          // Token is invalid or expired
          localStorage.removeItem('token');
          setAuthState({
            isAuthenticated: false,
            user: null,
          });
        });
    }
  }, []);

  const login = async (username: string, password: string) => {
    try {
      const response = await api.post('/auth/login', {
        username,
        password,
      });
      const { access_token } = response.data;
      localStorage.setItem('token', access_token);
      setAuthState({
        isAuthenticated: true,
        user: response.data.user,
      });
      return true;
    } catch (error) {
      console.error('Login error:', error);
      return false;
    }
  };

  const register = async (email: string, password: string) => {
    try {
      const response = await api.post('/auth/register', {
        email,
        password,
      });
      const { access_token } = response.data;
      localStorage.setItem('token', access_token);
      setAuthState({
        isAuthenticated: true,
        user: response.data.user,
      });
      return true;
    } catch (error) {
      console.error('Registration error:', error);
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setAuthState({
      isAuthenticated: false,
      user: null,
    });
  };

  return {
    ...authState,
    login,
    register,
    logout,
  };
}; 