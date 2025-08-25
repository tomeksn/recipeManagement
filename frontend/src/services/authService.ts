import { api } from './apiClient';
import { mockService } from './mockService';
import { 
  User, 
  LoginCredentials, 
  RegisterData, 
  TokenResponse 
} from '@/types/auth';

// Check if we're in offline mode
const isOfflineMode = import.meta.env.VITE_OFFLINE_MODE === 'true';
console.log('Auth service - offline mode:', isOfflineMode);
console.log('Environment VITE_OFFLINE_MODE:', import.meta.env.VITE_OFFLINE_MODE);

export const authService = {
  async login(credentials: LoginCredentials): Promise<TokenResponse> {
    if (isOfflineMode) {
      return mockService.login(credentials);
    }
    const response = await api.post<TokenResponse>('/auth/login', credentials);
    return response;
  },

  async register(data: RegisterData): Promise<TokenResponse> {
    if (isOfflineMode) {
      throw new Error('Registration not available in offline mode');
    }
    const response = await api.post<TokenResponse>('/auth/register', data);
    return response;
  },

  async logout(): Promise<void> {
    if (isOfflineMode) {
      return mockService.logout();
    }
    await api.post('/auth/logout');
  },

  async getCurrentUser(): Promise<User> {
    if (isOfflineMode) {
      return mockService.getCurrentUser();
    }
    const response = await api.get<User>('/auth/me');
    return response;
  },

  async refreshToken(refreshToken: string): Promise<TokenResponse> {
    const response = await api.post<TokenResponse>('/auth/refresh', {
      refresh_token: refreshToken,
    });
    return response;
  },

  async forgotPassword(email: string): Promise<void> {
    await api.post('/auth/forgot-password', { email });
  },

  async resetPassword(token: string, password: string): Promise<void> {
    await api.post('/auth/reset-password', { token, password });
  },

  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await api.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
  },

  async updateProfile(data: Partial<User>): Promise<User> {
    const response = await api.put<User>('/auth/profile', data);
    return response;
  },
};