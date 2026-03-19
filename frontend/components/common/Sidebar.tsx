'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState, useEffect } from 'react';
import { useAuthStore } from '@/lib/auth-store';

type NavItem = {
  label: string;
  href: string;
  icon: string;
  adminOnly?: boolean;   // hospital_admin, super_admin, super_owner (not department_admin)
  superOwnerOnly?: boolean;
  hospitalAdminOnly?: boolean;  // only hospital_admin (e.g. Create Department Admin)
};

const navItems: NavItem[] = [
  { label: 'Dashboard', href: '/dashboard', icon: '📊' },
  { label: 'Appointments', href: '/appointments', icon: '📅' },
  { label: 'Medical Records', href: '/medical-records', icon: '📋' },
  { label: 'Doctors', href: '/doctors', icon: '👨‍⚕️' },
  { label: 'Patients', href: '/patients', icon: '👥' },
  { label: 'Users', href: '/users', icon: '👤', adminOnly: true },
  { label: 'Create Department Admin', href: '/admin/create-department-admin', icon: '➕', hospitalAdminOnly: true },
  { label: 'Hospital Management', href: '/super-owner', icon: '🏥', superOwnerOnly: true },
  { label: 'Admin Settings', href: '/admin/settings', icon: '⚙️', adminOnly: true },
];

export function Sidebar() {
  const pathname = usePathname();
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const { user } = useAuthStore();

  useEffect(() => {
    if (isMobileOpen) document.body.style.overflow = 'hidden';
    else document.body.style.overflow = '';
    return () => { document.body.style.overflow = ''; };
  }, [isMobileOpen]);

  const filteredItems = navItems.filter((item) => {
    if (item.superOwnerOnly) return user?.role === 'super_owner';
    if (item.hospitalAdminOnly) return user?.role === 'hospital_admin';
    if (item.adminOnly) return ['admin', 'hospital_admin', 'super_admin', 'super_owner'].includes(user?.role || '');
    if (['super_owner'].includes(user?.role || '')) return ['Dashboard', 'Hospital Management', 'Admin Settings'].includes(item.label);
    if (item.label === 'Doctors') return user?.role !== 'doctor';
    if (item.label === 'Patients') return ['doctor', 'admin', 'hospital_admin', 'department_admin', 'super_admin'].includes(user?.role || '');
    return true;
  });

  const isActive = (href: string) => pathname.startsWith(href);

  return (
    <>
      {/* Mobile menu button - fixed top-left below header */}
      <div className="lg:hidden fixed top-14 left-4 z-30">
        <button
          type="button"
          onClick={() => setIsMobileOpen(!isMobileOpen)}
          className="p-2.5 rounded-xl bg-white border border-slate-200 shadow-soft hover:shadow-card-hover hover:bg-slate-50 transition-all duration-200"
          aria-label={isMobileOpen ? 'Close menu' : 'Open menu'}
        >
          <svg className="w-6 h-6 text-slate-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={isMobileOpen ? 'M6 18L18 6M6 6l12 12' : 'M4 6h16M4 12h16M4 18h16'} />
          </svg>
        </button>
      </div>

      {/* Overlay */}
      {isMobileOpen && (
        <div
          className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-20 lg:hidden transition-opacity duration-200"
          onClick={() => setIsMobileOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed lg:static inset-y-0 left-0 z-30
          w-72 max-w-[85vw] lg:w-64
          flex flex-col
          bg-gradient-to-b from-slate-800 to-slate-900 text-white
          transform transition-transform duration-300 ease-out
          lg:translate-x-0
          ${isMobileOpen ? 'translate-x-0 shadow-2xl' : '-translate-x-full'}
        `}
      >
        <div className="flex flex-col flex-1 overflow-y-auto p-5 lg:p-6">
          <div className="lg:hidden flex justify-end mb-4">
            <button
              type="button"
              onClick={() => setIsMobileOpen(false)}
              className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
              aria-label="Close menu"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div className="mb-8">
            <h2 className="text-xl font-bold tracking-tight text-white">CareFlow</h2>
            <p className="text-slate-400 text-sm mt-0.5">Hospital Management</p>
          </div>

          <nav className="space-y-1 flex-1">
            {filteredItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setIsMobileOpen(false)}
                className={`
                  flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200
                  ${isActive(item.href)
                    ? 'bg-primary-500 text-white shadow-glow'
                    : 'text-slate-300 hover:bg-white/10 hover:text-white'
                  }
                `}
              >
                <span className="text-lg" aria-hidden>{item.icon}</span>
                {item.label}
              </Link>
            ))}
          </nav>

          <div className="pt-4 mt-4 border-t border-slate-700">
            {user && (
              <div className="text-xs text-slate-400 space-y-0.5">
                <p className="font-medium text-slate-300 truncate">
                  {user.role === 'hospital_admin' && user.hospital_name
                    ? user.hospital_name
                    : user.role === 'department_admin' && user.department_name
                      ? `${user.name} (${user.department_name})`
                      : user.name}
                </p>
                <p className="truncate">{user.email}</p>
              </div>
            )}
          </div>
        </div>
      </aside>
    </>
  );
}
