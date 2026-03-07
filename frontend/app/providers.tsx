'use client';

import { useEffect } from 'react';
import { useAuthStore } from '@/lib/auth-store';

export function Providers({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    // Initialize auth store on client side
    useAuthStore.getState().initialize();
  }, []);

  return <>{children}</>;
}
