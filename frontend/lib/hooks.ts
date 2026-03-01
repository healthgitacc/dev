import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/auth-store';

/**
 * Hook to protect routes - redirects to login if not authenticated
 */
export const useProtectedRoute = () => {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuthStore();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoading, router]);

  return { isAuthenticated, isLoading };
};

/**
 * Hook to check user role
 */
export const useRole = () => {
  const { user } = useAuthStore();
  return {
    role: user?.role,
    isAdmin: user?.role === 'admin',
    isDoctor: user?.role === 'doctor',
    isPatient: user?.role === 'patient',
  };
};

/**
 * Hook to check authorization for specific roles
 */
export const useAuthorizedRoute = (allowedRoles: string[]) => {
  const router = useRouter();
  const { user, isLoading } = useAuthStore();

  useEffect(() => {
    if (!isLoading) {
      if (!user) {
        router.push('/login');
      } else if (!allowedRoles.includes(user.role)) {
        router.push('/dashboard');
      }
    }
  }, [user, isLoading, router, allowedRoles]);

  return { isAuthorized: user && allowedRoles.includes(user.role), isLoading };
};

/**
 * Hook to get current user
 */
export const useCurrentUser = () => {
  const { user } = useAuthStore();
  return user;
};
