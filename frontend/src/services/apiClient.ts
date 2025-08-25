import axios, { 
  AxiosInstance, 
  AxiosRequestConfig, 
  AxiosResponse, 
  AxiosError 
} from 'axios';
import { toast } from 'react-hot-toast';

import { ApiError } from '@/types/api';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

console.log('API Client - base URL:', import.meta.env.VITE_API_URL);
console.log('API Client - offline mode:', import.meta.env.VITE_OFFLINE_MODE);

// Development mode - add offline detection
const isDevelopmentOffline = import.meta.env.DEV && import.meta.env.VITE_OFFLINE_MODE === 'true';

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Add request ID for tracking
    config.headers['X-Request-ID'] = crypto.randomUUID();
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error: AxiosError<ApiError>) => {
    // Handle network errors
    if (!error.response) {
      toast.error('Network error. Please check your connection.');
      return Promise.reject({
        message: 'Network error',
        status_code: 0,
      });
    }

    const { status, data } = error.response;

    // Handle specific status codes
    switch (status) {
      case 401:
        // Unauthorized - clear token and redirect to login
        localStorage.removeItem('auth_token');
        window.location.href = '/login';
        break;
      
      case 403:
        toast.error('You don\'t have permission to perform this action.');
        break;
      
      case 404:
        // Don't show toast for 404s - let components handle it
        break;
      
      case 429:
        toast.error('Too many requests. Please try again later.');
        break;
      
      case 500:
      case 502:
      case 503:
      case 504:
        toast.error('Server error. Please try again later.');
        break;
      
      default:
        if (data?.message) {
          toast.error(data.message);
        } else {
          toast.error('An unexpected error occurred.');
        }
    }

    return Promise.reject(data || {
      message: 'Request failed',
      status_code: status,
    });
  }
);

// Helper methods
export const api = {
  get: <T = any>(url: string, config?: AxiosRequestConfig) =>
    apiClient.get<T>(url, config).then(response => response.data),
  
  post: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) =>
    apiClient.post<T>(url, data, config).then(response => response.data),
  
  put: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) =>
    apiClient.put<T>(url, data, config).then(response => response.data),
  
  patch: <T = any>(url: string, data?: any, config?: AxiosRequestConfig) =>
    apiClient.patch<T>(url, data, config).then(response => response.data),
  
  delete: <T = any>(url: string, config?: AxiosRequestConfig) =>
    apiClient.delete<T>(url, config).then(response => response.data),
};

export { apiClient };
export default api;