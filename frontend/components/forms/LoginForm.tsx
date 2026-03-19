'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import Link from 'next/link';
import { loginSchema, type LoginFormData } from '@/lib/validation';
import { useAuthStore } from '@/lib/auth-store';
import { apiClient, setAuthToken } from '@/lib/api';
import { API_ENDPOINTS, ERROR_MESSAGES } from '@/lib/constants';
import { AuthResponse } from '@/lib/types';

export function LoginForm() {
  const router = useRouter();
  const [serverError, setServerError] = useState<string | null>(null);
  const setUser = useAuthStore((state) => state.setUser);
  const setToken = useAuthStore((state) => state.setToken);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    try {
      setServerError(null);

      console.log('[LoginForm] Submitting login request with email:', data.email);

      const response = await apiClient.post<any>(
        API_ENDPOINTS.AUTH_LOGIN,
        data
      );

      console.log('[LoginForm] Login response received:', response.data);

      // Handle both response structures (full user object or individual fields)
      const responseData = response.data;
      const access_token = responseData.access_token;
      
      if (!access_token) {
        throw new Error('No access token in response');
      }

      // Construct user object from response (backend returns name, email, phone, hospital_name in TokenResponse)
      const user = {
        id: responseData.user?.id ?? responseData.user_id ?? 0,
        name: responseData.user?.name ?? responseData.name ?? 'User',
        email: responseData.user?.email ?? responseData.email ?? '',
        phone: responseData.user?.phone ?? responseData.phone ?? '',
        role: responseData.user?.role ?? responseData.role ?? 'patient',
        is_active: responseData.user?.is_active !== undefined ? responseData.user.is_active : true,
        created_at: responseData.user?.created_at ?? new Date().toISOString(),
        updated_at: responseData.user?.updated_at ?? new Date().toISOString(),
        ...(responseData.hospital_name != null && { hospital_name: responseData.hospital_name }),
        ...(responseData.department_id != null && { department_id: responseData.department_id }),
        ...(responseData.department_name != null && { department_name: responseData.department_name }),
      };

      console.log('[LoginForm] Constructed user object:', user);

      if (!user.id || !user.email) {
        throw new Error(`Invalid user data: id=${user.id}, email=${user.email}`);
      }

      console.log('[LoginForm] Setting auth token in cookies');
      // Store token in cookie
      setAuthToken(access_token);
      
      // Store user in localStorage
      if (typeof window !== 'undefined') {
        try {
          localStorage.setItem('hospital_auth_user', JSON.stringify(user));
          console.log('[LoginForm] Stored user in localStorage');
        } catch (e) {
          console.error('[LoginForm] Error storing user in localStorage:', e);
        }
      }

      console.log('[LoginForm] Updating auth store');
      // Update auth store (this should also trigger state updates)
      setToken(access_token);
      setUser(user);

      console.log('[LoginForm] Auth store updated, redirecting to dashboard');
      // Give state a moment to update before redirecting
      await new Promise(resolve => setTimeout(resolve, 100));

      // Redirect to dashboard
      router.push('/dashboard');
    } catch (error: any) {
      console.error('[LoginForm] Error during login:', error);
      console.error('[LoginForm] Error details:', {
        message: error.message,
        code: error.code,
        response: error.response,
        isAxiosError: error.isAxiosError,
        status: error.response?.status,
        data: error.response?.data,
      });
      
      if (error.response?.data?.detail) {
        setServerError(
          typeof error.response.data.detail === 'string'
            ? error.response.data.detail
            : ERROR_MESSAGES.INVALID_CREDENTIALS
        );
      } else if (error.message) {
        setServerError(error.message);
      } else {
        setServerError(ERROR_MESSAGES.NETWORK_ERROR + ' - ' + JSON.stringify(error));
      }
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
      {serverError && (
        <div className="rounded-xl bg-red-50 border border-red-200 p-4">
          <p className="text-sm text-red-700">{serverError}</p>
        </div>
      )}

      <div>
        <label htmlFor="email" className="block text-sm font-medium text-slate-700 mb-1.5">
          Email
        </label>
        <input
          {...register('email')}
          id="email"
          type="email"
          placeholder="you@example.com"
          className={`input-base ${errors.email ? 'border-red-400 focus:ring-red-500/20 focus:border-red-500' : ''}`}
        />
        {errors.email && <p className="mt-1.5 text-sm text-red-600">{errors.email.message}</p>}
      </div>

      <div>
        <label htmlFor="password" className="block text-sm font-medium text-slate-700 mb-1.5">
          Password
        </label>
        <input
          {...register('password')}
          id="password"
          type="password"
          placeholder="••••••••"
          className={`input-base ${errors.password ? 'border-red-400 focus:ring-red-500/20 focus:border-red-500' : ''}`}
        />
        {errors.password && <p className="mt-1.5 text-sm text-red-600">{errors.password.message}</p>}
      </div>

      <div className="flex items-center justify-between">
        <label className="flex items-center gap-2 cursor-pointer">
          <input type="checkbox" className="h-4 w-4 rounded border-slate-300 text-primary-600 focus:ring-primary-500" />
          <span className="text-sm text-slate-600">Remember me</span>
        </label>
        <Link href="/forgot-password" className="text-sm text-primary-600 hover:text-primary-700 font-medium">
          Forgot password?
        </Link>
      </div>

      <button type="submit" disabled={isSubmitting} className="btn-primary w-full py-3">
        {isSubmitting ? 'Signing in...' : 'Sign in'}
      </button>

      <p className="text-center text-sm text-slate-600">
        Don&apos;t have an account?{' '}
        <Link href="/register" className="text-primary-600 hover:text-primary-700 font-medium">
          Sign up
        </Link>
      </p>
    </form>
  );
}
