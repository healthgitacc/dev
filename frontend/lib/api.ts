import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import Cookies from 'js-cookie';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const TOKEN_KEY = 'hospital_auth_token';

console.log('[API Client] Initializing with API_URL:', API_URL);

/**
 * Create and configure axios instance with interceptors
 */
const createApiClient = (): AxiosInstance => {
  const client = axios.create({
    baseURL: API_URL,
    timeout: 60000, // Increased from 30s to 60s for slower queries
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Request interceptor - add token
  client.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
      const token = Cookies.get(TOKEN_KEY);
      console.log('[API Client] Request interceptor - token exists:', !!token);
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => {
      console.error('[API Client] Request interceptor error:', error);
      return Promise.reject(error);
    }
  );

  // Response interceptor - handle errors
  client.interceptors.response.use(
    (response) => {
      console.log('[API Client] Response received:', response.status);
      return response;
    },
    (error: AxiosError) => {
      console.error('[API Client] Response error:', {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message,
        code: error.code,
      });
      if (error.response?.status === 401) {
        // Token expired or invalid
        Cookies.remove(TOKEN_KEY);
        typeof window !== 'undefined' && window.location.replace('/login');
      }
      return Promise.reject(error);
    }
  );

  return client;
};

export const apiClient = createApiClient();

/**
 * Get stored auth token
 */
export const getAuthToken = (): string | undefined => {
  if (typeof window === 'undefined') return undefined;
  return Cookies.get(TOKEN_KEY);
};

/**
 * Set auth token
 */
export const setAuthToken = (token: string): void => {
  Cookies.set(TOKEN_KEY, token, {
    expires: 1, // 1 day
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'Strict',
  });
};

/**
 * Clear auth token
 */
export const clearAuthToken = (): void => {
  Cookies.remove(TOKEN_KEY);
};

export default apiClient;
