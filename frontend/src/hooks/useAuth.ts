import { useState, useEffect } from 'react';
import { auth } from '../services/api';

interface AuthState {
  isAuthenticated: boolean;
  user: any | null;
  isLoading: boolean;
}

export const useAuth = () => {
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    user: null,
    isLoading: true,
  });

  useEffect(() => {
    const verifyToken = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          const user = await auth.getCurrentUser();
          setAuthState({
            isAuthenticated: true,
            user,
            isLoading: false,
          });
        } catch (error) {
          console.error('Token verification failed:', error);
          localStorage.removeItem('token');
          setAuthState({
            isAuthenticated: false,
            user: null,
            isLoading: false,
          });
        }
      } else {
        setAuthState({
          isAuthenticated: false,
          user: null,
          isLoading: false,
        });
      }
    };

    // Handle token expiration
    const handleTokenExpiration = () => {
      localStorage.removeItem('token');
      setAuthState({
        isAuthenticated: false,
        user: null,
        isLoading: false,
      });
      // Dispatch a custom event for navigation
      window.dispatchEvent(new Event('auth:logout'));
    };

    // Listen for token expiration events
    window.addEventListener('auth:expired', handleTokenExpiration);

    // Initial token verification
    verifyToken();

    // Cleanup
    return () => {
      window.removeEventListener('auth:expired', handleTokenExpiration);
    };
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const response = await auth.login(email, password);
      const { access_token } = response;
      localStorage.setItem('token', access_token);
      const user = await auth.getCurrentUser();
      setAuthState({
        isAuthenticated: true,
        user,
        isLoading: false,
      });
      return true;
    } catch (error) {
      console.error('Login error:', error);
      return false;
    }
  };

  const register = async (username: string, email: string, password: string) => {
    try {
      const user = await auth.register(username, email, password);
      const response = await auth.login(email, password);
      const { access_token } = response;
      localStorage.setItem('token', access_token);
      setAuthState({
        isAuthenticated: true,
        user,
        isLoading: false,
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
      isLoading: false,
    });
    // Dispatch a custom event for navigation
    window.dispatchEvent(new Event('auth:logout'));
  };

  return {
    ...authState,
    login,
    register,
    logout,
  };
}; 