// Authentication types
export interface User {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'user' | 'viewer';
  avatar?: string;
  preferences?: UserPreferences;
  created_at: string;
  last_login?: string;
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'auto';
  language: string;
  timezone: string;
  view_mode: 'card' | 'list' | 'table';
  items_per_page: number;
  notifications: {
    email: boolean;
    push: boolean;
    in_app: boolean;
  };
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface LoginCredentials {
  email: string;
  password: string;
  remember_me?: boolean;
}

export interface RegisterData {
  name: string;
  email: string;
  password: string;
  confirm_password: string;
  terms_accepted: boolean;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: 'Bearer';
  expires_in: number;
  user: User;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

// Permission types
export type Permission = 
  | 'products:read'
  | 'products:write'
  | 'products:delete'
  | 'recipes:read' 
  | 'recipes:write'
  | 'recipes:delete'
  | 'calculations:read'
  | 'calculations:write'
  | 'admin:users'
  | 'admin:settings';

export interface Role {
  name: string;
  permissions: Permission[];
}

// Route protection
export interface ProtectedRouteProps {
  children: React.ReactNode;
  permissions?: Permission[];
  fallback?: React.ReactNode;
}