'use client';

import { useState, useRef, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/auth-store';
import { ROLE_LABELS } from '@/lib/constants';

export function Header() {
  const router = useRouter();
  const { user, logout } = useAuthStore();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) setShowUserMenu(false);
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  const displayName =
    user?.role === 'hospital_admin' && user?.hospital_name
      ? user.hospital_name
      : user?.role === 'department_admin' && user?.department_name
        ? `${user.name} (${user.department_name})`
        : (user?.name || 'User');

  return (
    <header className="sticky top-0 z-10 flex h-14 items-center border-b border-slate-200/80 bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/80">
      <div className="container-app flex items-center justify-between gap-4">
        <Link
          href="/dashboard"
          className="flex items-center gap-2 shrink-0 text-slate-800 hover:text-primary-600 transition-colors"
        >
          <span className="text-2xl" aria-hidden>🏥</span>
          <span className="text-lg font-semibold hidden sm:inline">CareFlow</span>
        </Link>

        <div className="flex items-center gap-2 sm:gap-4 ml-auto">
          {user && (
            <>
              <div className="hidden sm:block text-right min-w-0">
                <p className="text-sm font-medium text-slate-800 truncate max-w-[140px]">{displayName}</p>
                <p className="text-xs text-slate-500">{ROLE_LABELS[user.role] || user.role?.replace('_', ' ') || 'User'}</p>
              </div>

              <div className="relative" ref={menuRef}>
                <button
                  type="button"
                  onClick={() => setShowUserMenu(!showUserMenu)}
                  className="flex items-center justify-center w-10 h-10 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 transition-colors"
                  aria-expanded={showUserMenu}
                  aria-haspopup="true"
                >
                  <span className="text-lg" aria-hidden>👤</span>
                </button>

                {showUserMenu && (
                  <div className="absolute right-0 mt-2 w-52 rounded-xl bg-white border border-slate-200 shadow-soft py-1 z-50 animate-fade-in">
                    <Link
                      href="/profile"
                      className="block px-4 py-2.5 text-sm text-slate-700 hover:bg-slate-50 rounded-lg mx-1"
                      onClick={() => setShowUserMenu(false)}
                    >
                      Change Password
                    </Link>
                    <div className="my-1 border-t border-slate-100" />
                    <button
                      type="button"
                      onClick={handleLogout}
                      className="w-full text-left px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 rounded-lg mx-1"
                    >
                      Logout
                    </button>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
