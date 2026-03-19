'use client';

import { useEffect, useState } from 'react';
import { StatCard } from '@/components/cards/StatCard';
import { useAuthStore } from '@/lib/auth-store';
import apiClient from '@/lib/api';
import LoadingSpinner from '@/components/common/LoadingSpinner';

interface DashboardStats {
  total_patients: number;
  total_doctors: number;
  total_appointments: number;
  completed_appointments: number;
}

export default function DashboardPage() {
  const { user, token, isLoading } = useAuthStore();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [pageLoading, setPageLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isLoading) {
      console.log('Auth is loading...');
      return;
    }

    if (!user) {
      console.log('No user found, redirecting to login');
      setError('Not authenticated. Please log in.');
      setPageLoading(false);
      return;
    }

    const fetchDashboardData = async () => {
      try {
        console.log('Fetching dashboard stats for user:', user.email);
        setPageLoading(true);
        setError(null);

        // Fetch dashboard stats from backend
        console.time('Dashboard API Call');
        const response = await apiClient.get('/api/admin/dashboard-stats');
        console.timeEnd('Dashboard API Call');

        console.log('Dashboard stats response:', response.data);
        if (response.data) {
          setStats(response.data);
        } else {
          setError('No data received from server');
        }
      } catch (err: any) {
        console.error('Failed to load dashboard:', err);
        
        let errorMessage = 'Failed to load dashboard data';
        
        // Better error messages
        if (err.code === 'ECONNABORTED' || err.message.includes('timeout')) {
          errorMessage = 'Request timeout (60s exceeded). Backend may be slow or unavailable.';
        } else if (err.code === 'ECONNREFUSED') {
          errorMessage = 'Cannot connect to backend server. Make sure it\'s running on port 8000.';
        } else if (err.response?.status === 401) {
          errorMessage = 'Unauthorized. Please log in again.';
        } else if (err.response?.status === 403) {
          errorMessage = 'You don\'t have permission to view the dashboard.';
        } else if (err.response?.status === 404) {
          errorMessage = 'Dashboard endpoint not found on server.';
        } else if (err.response?.status === 500) {
          errorMessage = 'Server error. Please try again later.';
        } else {
          errorMessage = 
            err.response?.data?.message || 
            err.response?.data?.detail || 
            err.message || 
            errorMessage;
        }
        
        setError(errorMessage);
      } finally {
        setPageLoading(false);
      }
    };

    fetchDashboardData();
  }, [token, isLoading, user]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" text="Authenticating..." />
      </div>
    );
  }

  if (pageLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner size="lg" text="Loading dashboard..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="card p-6 border-red-200 bg-red-50/50">
        <h2 className="text-lg font-semibold text-red-900 mb-2">Error Loading Dashboard</h2>
        <p className="text-red-700 mb-4">{error}</p>
        <div className="flex flex-wrap gap-3">
          <button type="button" onClick={() => window.location.reload()} className="btn-primary bg-red-600 hover:bg-red-700 focus:ring-red-500">
            Retry
          </button>
          <a href="/" className="btn-secondary">Go Home</a>
        </div>
        <p className="text-sm text-red-600 mt-4">
          {error.includes('timeout') && 'Tip: The backend may be busy. Try again in a moment.'}
          {error.includes('ECONNREFUSED') && 'Tip: Start the backend server on port 8000.'}
        </p>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="card p-6 border-amber-200 bg-amber-50/50">
        <h2 className="text-lg font-semibold text-amber-900 mb-2">No Data Available</h2>
        <p className="text-amber-800">Dashboard statistics could not be loaded. Try refreshing the page.</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold text-slate-900">Dashboard</h1>
        <p className="mt-2 text-slate-600">
          Welcome back, {user?.name}. Here&apos;s what&apos;s happening today.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4 sm:gap-6">
        <StatCard title="Total Patients" value={stats?.total_patients ?? 0} icon="👥" description="System-wide" href="/patients" />
        <StatCard title="Total Doctors" value={stats?.total_doctors ?? 0} icon="👨‍⚕️" description="System-wide" href="/doctors" />
        <StatCard title="Total Appointments" value={stats?.total_appointments ?? 0} icon="📅" description="All time" href="/appointments" />
        <StatCard title="Completed" value={stats?.completed_appointments ?? 0} icon="✓" description="Appointments" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="card p-6">
          <h2 className="text-lg font-semibold text-slate-900 mb-5">Quick Actions</h2>
          <div className="space-y-3">
            <a href="/appointments" className="btn-primary w-full flex items-center justify-center gap-2">
              <span>📅</span> View Appointments
            </a>
            <a href="/medical-records" className="btn-secondary w-full flex items-center justify-center gap-2">
              <span>📋</span> Medical Records
            </a>
            <a href="/doctors" className="btn-secondary w-full flex items-center justify-center gap-2">
              <span>👨‍⚕️</span> Find Doctor
            </a>
            <a href="/profile" className="btn-secondary w-full flex items-center justify-center gap-2">
              <span>👤</span> My Profile
            </a>
          </div>
        </div>
        <div className="lg:col-span-2 card p-6">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">System Overview</h2>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between py-2 border-b border-slate-100">
              <span className="text-slate-500">Role</span>
              <span className="font-medium text-slate-800 capitalize">{user?.role?.replace('_', ' ')}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-slate-100">
              <span className="text-slate-500">Email</span>
              <span className="font-medium text-slate-800 truncate max-w-[200px]">{user?.email}</span>
            </div>
            <div className="flex justify-between py-2">
              <span className="text-slate-500">Status</span>
              <span className="font-medium text-emerald-600">Active</span>
            </div>
          </div>
          <p className="text-xs text-slate-400 mt-4">CareFlow v1.0</p>
        </div>
      </div>

      <div className="rounded-2xl bg-primary-50 border border-primary-100 p-6">
        <h3 className="text-lg font-semibold text-primary-900 mb-2">Getting started</h3>
        <p className="text-primary-800 mb-4">
          Use the menu to manage appointments, view medical records, and connect with healthcare staff.
        </p>
        <ul className="text-sm text-primary-700 space-y-1 list-disc list-inside">
          <li>View and manage your appointments</li>
          <li>Access medical records and history</li>
          <li>Find and book with doctors</li>
          <li>Update profile and password</li>
        </ul>
      </div>
    </div>
  );
}
