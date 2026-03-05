'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/auth-store';

export interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: string | string[];
}

/**
 * Protected Route Component
 * Ensures user is authenticated before rendering content
 */
export function ProtectedRoute({ children, requiredRole }: ProtectedRouteProps) {
  const router = useRouter();
  const { isAuthenticated, user, isLoading } = useAuthStore();
  const [hasChecked, setHasChecked] = useState(false);

  useEffect(() => {
    // Don't do anything while loading
    if (isLoading) {
      return;
    }

    setHasChecked(true);

    // Redirect to login if not authenticated
    if (!isAuthenticated) {
      router.replace('/login');
      return;
    }

    // Check role if required
    if (requiredRole && user) {
      const roles = Array.isArray(requiredRole) ? requiredRole : [requiredRole];
      if (!roles.includes(user.role)) {
        router.replace('/dashboard');
      }
    }
  }, [isAuthenticated, isLoading, user, requiredRole, router]);

  // Show loading spinner during auth initialization
  if (isLoading || !hasChecked) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Don't render anything if not authenticated (redirecting)
  if (!isAuthenticated) {
    return null;
  }

  // Check role restriction
  if (requiredRole && user) {
    const roles = Array.isArray(requiredRole) ? requiredRole : [requiredRole];
    if (!roles.includes(user.role)) {
      return null;
    }
  }

  // Render children only when authenticated
  return <>{children}</>;
}

/**
 * Role Guard Component
 * Conditionally renders content based on user role
 */
export function RoleGuard({
  children,
  requiredRole,
}: {
  children: React.ReactNode;
  requiredRole: string | string[];
}) {
  const { user } = useAuthStore();

  if (!user) {
    return null;
  }

  const roles = Array.isArray(requiredRole) ? requiredRole : [requiredRole];
  if (!roles.includes(user.role)) {
    return null;
  }

  return <>{children}</>;
}
