'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState } from 'react';
import { useAuthStore } from '@/lib/auth-store';

type NavItem = {
  label: string;
  href: string;
  icon: string;
  adminOnly?: boolean;
};

const navItems: NavItem[] = [
  { label: 'Dashboard', href: '/dashboard', icon: '📊' },
  { label: 'Appointments', href: '/appointments', icon: '📅' },
  { label: 'Medical Records', href: '/medical-records', icon: '📋' },
  { label: 'Doctors', href: '/doctors', icon: '👨‍⚕️' },
  { label: 'Patients', href: '/patients', icon: '👥' },
  { label: 'Users', href: '/users', icon: '👤', adminOnly: true },
  { label: 'Admin Settings', href: '/admin/settings', icon: '⚙️', adminOnly: true },
];

export function Sidebar() {
  const pathname = usePathname();
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const { user } = useAuthStore();

  // Filter nav items based on role
  const filteredItems = navItems.filter((item) => {
    // Admin-only items
    if (item.adminOnly) {
      return user?.role === 'admin' || user?.role === 'hospital_admin' || user?.role === 'super_admin';
    }
    // Doctors link - hide for doctors
    if (item.label === 'Doctors') {
      return user?.role !== 'doctor';
    }
    // Patients link - show for doctors and admins
    if (item.label === 'Patients') {
      return user?.role === 'doctor' || user?.role === 'admin' || user?.role === 'hospital_admin' || user?.role === 'super_admin';
    }
    return true;
  });

  const isActive = (href: string) => {
    return pathname.startsWith(href);
  };

  return (
    <>
      {/* Mobile menu button */}
      <div className="lg:hidden fixed top-20 left-4 z-30">
        <button
          onClick={() => setIsMobileOpen(!isMobileOpen)}
          className="p-2 rounded-lg bg-white shadow-md hover:bg-gray-50"
        >
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d={isMobileOpen ? 'M6 18L18 6M6 6l12 12' : 'M4 6h16M4 12h16M4 18h16'}
            />
          </svg>
        </button>
      </div>

      {/* Sidebar */}
      <aside
        className={`${
          isMobileOpen ? 'translate-x-0' : '-translate-x-full'
        } lg:translate-x-0 fixed lg:static top-0 left-0 w-64 h-screen bg-gray-900 text-white p-6 transition-transform duration-200 ease-in-out z-20`}
      >
        {/* Close button (mobile) */}
        <div className="lg:hidden mb-8 flex justify-end">
          <button
            onClick={() => setIsMobileOpen(false)}
            className="text-gray-400 hover:text-white"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Logo */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold tracking-tight">🏥 Hospital</h2>
          <p className="text-gray-400 text-sm">Management System</p>
        </div>

        {/* Navigation */}
        <nav className="space-y-2">
          {filteredItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              onClick={() => setIsMobileOpen(false)}
              className={`block px-4 py-3 rounded-lg transition-colors ${
                isActive(item.href)
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:bg-gray-800'
              }`}
            >
              <span className="mr-3">{item.icon}</span>
              {item.label}
            </Link>
          ))}
        </nav>

        {/* Footer */}
        <div className="absolute bottom-6 left-6 right-6">
          <div className="text-xs text-gray-500 border-t border-gray-700 pt-4">
            {user && (
              <>
                <p className="font-medium text-gray-300 mb-2">{user.name}</p>
                <p>{user.email}</p>
              </>
            )}
          </div>
        </div>
      </aside>

      {/* Mobile overlay */}
      {isMobileOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-10 lg:hidden"
          onClick={() => setIsMobileOpen(false)}
        />
      )}
    </>
  );
}
