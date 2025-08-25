import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { toast } from 'react-hot-toast';

import { User, AuthState, LoginCredentials, RegisterData } from '@/types/auth';
import { authService } from '@/services/authService';

// Auth actions
type AuthAction =
  | { type: 'AUTH_START' }
  | { type: 'AUTH_SUCCESS'; payload: { user: User; token: string } }
  | { type: 'AUTH_FAILURE'; payload: string }
  | { type: 'LOGOUT' }
  | { type: 'CLEAR_ERROR' };

// Auth reducer
function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'AUTH_START':
      return { ...state, isLoading: true, error: null };
    
    case 'AUTH_SUCCESS':
      return {
        ...state,
        isLoading: false,
        isAuthenticated: true,
        user: action.payload.user,
        token: action.payload.token,
        error: null,
      };
    
    case 'AUTH_FAILURE':
      return {
        ...state,
        isLoading: false,
        isAuthenticated: false,
        user: null,
        token: null,
        error: action.payload,
      };
    
    case 'LOGOUT':
      return {
        ...state,
        isLoading: false,
        isAuthenticated: false,
        user: null,
        token: null,
        error: null,
      };
    
    case 'CLEAR_ERROR':
      return { ...state, error: null };
    
    default:
      return state;
  }
}

// Initial state
const initialState: AuthState = {
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,
};

// Auth context
interface AuthContextValue extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

interface AuthProviderProps {
  children: React.ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Check for existing auth on mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = localStorage.getItem('auth_token');
        if (!token) {
          dispatch({ type: 'AUTH_FAILURE', payload: 'No token found' });
          return;
        }

        // Validate token and get user info
        const user = await authService.getCurrentUser();
        dispatch({ type: 'AUTH_SUCCESS', payload: { user, token } });
      } catch (error) {
        localStorage.removeItem('auth_token');
        dispatch({ type: 'AUTH_FAILURE', payload: 'Token validation failed' });
      }
    };

    checkAuth();
  }, []);

  const login = async (credentials: LoginCredentials) => {
    try {
      dispatch({ type: 'AUTH_START' });
      
      const response = await authService.login(credentials);
      
      // Store token
      localStorage.setItem('auth_token', response.access_token);
      
      dispatch({
        type: 'AUTH_SUCCESS',
        payload: {
          user: response.user,
          token: response.access_token,
        },
      });

      toast.success(`Welcome back, ${response.user.name}!`);
    } catch (error: any) {
      const message = error?.response?.data?.message || 'Login failed';
      dispatch({ type: 'AUTH_FAILURE', payload: message });
      toast.error(message);
    }
  };

  const register = async (data: RegisterData) => {
    try {
      dispatch({ type: 'AUTH_START' });
      
      const response = await authService.register(data);
      
      // Store token
      localStorage.setItem('auth_token', response.access_token);
      
      dispatch({
        type: 'AUTH_SUCCESS',
        payload: {
          user: response.user,
          token: response.access_token,
        },
      });

      toast.success(`Welcome to Recipe Management, ${response.user.name}!`);
    } catch (error: any) {
      const message = error?.response?.data?.message || 'Registration failed';
      dispatch({ type: 'AUTH_FAILURE', payload: message });
      toast.error(message);
    }
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    dispatch({ type: 'LOGOUT' });
    toast.success('Logged out successfully');
  };

  const clearError = () => {
    dispatch({ type: 'CLEAR_ERROR' });
  };

  const contextValue: AuthContextValue = {
    ...state,
    login,
    register,
    logout,
    clearError,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}