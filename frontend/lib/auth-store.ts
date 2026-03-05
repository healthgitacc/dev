import { create } from 'zustand';
import Cookies from 'js-cookie';

export type UserRole = 'admin' | 'doctor' | 'patient' | 'hospital_admin' | 'super_admin';

export interface User {
  id: number;
  name: string;
  email: string;
  phone: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  logout: () => void;
  initialize: () => void;
}

const TOKEN_KEY = 'hospital_auth_token';
const USER_KEY = 'hospital_auth_user';

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,

  setUser: (user) => {
    set({ user, isAuthenticated: !!user });
    if (user && typeof window !== 'undefined') {
      localStorage.setItem(USER_KEY, JSON.stringify(user));
    }
  },
  setToken: (token) => {
    set({
      token,
      isAuthenticated: !!token,
    });
    if (token && typeof window !== 'undefined') {
      import('js-cookie').then(m => m.default.set(TOKEN_KEY, token, {
        expires: 1,
        sameSite: 'Strict',
      }));
    }
  },

  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),

  logout: () => {
    Cookies.remove(TOKEN_KEY);
    typeof window !== 'undefined' && localStorage.removeItem(USER_KEY);
    set({
      user: null,
      token: null,
      isAuthenticated: false,
      error: null,
    });
  },

  initialize: () => {
    try {
      if (typeof window === 'undefined') {
        set({ isLoading: false });
        return;
      }

      const token = Cookies.get(TOKEN_KEY);
      const userJson = localStorage.getItem(USER_KEY);

      if (token && userJson) {
        const user = JSON.parse(userJson);
        set({
          token,
          user,
          isAuthenticated: true,
          isLoading: false,
        });
      } else {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          isLoading: false,
        });
      }
    } catch (error) {
      console.error('Auth initialization error:', error);
      try {
        Cookies.remove(TOKEN_KEY);
        localStorage.removeItem(USER_KEY);
      } catch (e) {
        console.error('Error cleaning up auth:', e);
      }
      set({
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
      });
    }
  },
}));
