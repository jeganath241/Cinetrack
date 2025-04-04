import { useState, useEffect } from 'react';
import { auth } from '../services/api';
import { useNavigate } from 'react-router-dom';

interface AuthState {
  isAuthenticated: boolean;
  user: any | null;
  isLoading: boolean;
}

export const useAuth = () => {
  const navigate = useNavigate();
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: !!localStorage.getItem('token'),
    user: null,
    isLoading: true,
  });

  useEffect(() => {
    const verifyToken = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        setAuthState({
          isAuthenticated: false,
          user: null,
          isLoading: false,
        });
        return;
      }

      try {
        const user = await auth.getCurrentUser();
        setAuthState({
          isAuthenticated: true,
          user,
          isLoading: false,
        });
      } catch (error) {
        console.error('Token verification failed:', error);
        handleLogout();
      }
    };

    const handleLogout = () => {
      localStorage.removeItem('token');
      setAuthState({
        isAuthenticated: false,
        user: null,
        isLoading: false,
      });
    };

    // Initial token verification
    verifyToken();

    // Listen for auth events
    const handleAuthLogout = () => {
      handleLogout();
      navigate('/login');
    };

    window.addEventListener('auth:logout', handleAuthLogout);

    // Set up periodic token verification (every minute)
    const verificationInterval = setInterval(verifyToken, 60 * 1000);

    // Cleanup
    return () => {
      window.removeEventListener('auth:logout', handleAuthLogout);
      clearInterval(verificationInterval);
    };
  }, [navigate]);

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
      navigate('/home');
      return true;
    } catch (error) {
      console.error('Login error:', error);
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
    navigate('/login');
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
      navigate('/home');
      return true;
    } catch (error) {
      console.error('Registration error:', error);
      return false;
    }
  };

  return {
    ...authState,
    login,
    logout,
    register,
  };
};