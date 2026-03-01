'use client';

import { useEffect, useState } from 'react';
import { StatCard } from '@/components/cards/StatCard';
import { useAuthStore } from '@/lib/auth-store';
import apiClient from '@/lib/api';

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
        const response = await apiClient.get('/api/admin/dashboard-stats');

        console.log('Dashboard stats response:', response.data);
        if (response.data) {
          setStats(response.data);
        } else {
          setError('No data received from server');
        }
      } catch (err: any) {
        console.error('Failed to load dashboard:', err);
        const errorMessage = 
          err.response?.data?.message || 
          err.response?.data?.detail || 
          err.message || 
          'Failed to load dashboard data';
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
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Authenticating...</p>
        </div>
      </div>
    );
  }

  if (pageLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-red-900 mb-2">Error Loading Dashboard</h2>
          <p className="text-red-700 mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="p-6">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-yellow-900 mb-2">No Data Available</h2>
          <p className="text-yellow-700">Dashboard statistics could not be loaded. Please try refreshing the page.</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Welcome back, {user?.name}! Here's what's happening with your account today.
        </p>
      </div>

      {/* Statistics Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        <StatCard
          title="Total Patients"
          value={stats?.total_patients || 0}
          icon="👥"
          description="System-wide"
        />
        <StatCard
          title="Total Doctors"
          value={stats?.total_doctors || 0}
          icon="👨‍⚕️"
          description="System-wide"
        />
        <StatCard
          title="Total Appointments"
          value={stats?.total_appointments || 0}
          icon="📅"
          description="All time"
        />
        <StatCard
          title="Completed"
          value={stats?.completed_appointments || 0}
          icon="✓"
          description="Appointments"
        />
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 mb-6">
            Quick Actions
          </h2>

          <div className="space-y-3">
            <a
              href="/appointments"
              className="block w-full px-4 py-3 text-center bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              📅 View Appointments
            </a>
            <a
              href="/medical-records"
              className="block w-full px-4 py-3 text-center border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
            >
              📋 Medical Records
            </a>
            <a
              href="/doctors"
              className="block w-full px-4 py-3 text-center border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
            >
              👨‍⚕️ Find Doctor
            </a>
            <a
              href="/profile"
              className="block w-full px-4 py-3 text-center border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
            >
              👤 My Profile
            </a>
          </div>
        </div>

        {/* System Info */}
        <div className="lg:col-span-2 bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            System Overview
          </h2>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">User Role:</span>
              <span className="font-medium text-gray-900 capitalize">{user?.role}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Email:</span>
              <span className="font-medium text-gray-900">{user?.email}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Status:</span>
              <span className="font-medium text-green-600">Active</span>
            </div>
            <hr className="my-3" />
            <p className="text-gray-500">Hospital Management System - v1.0</p>
          </div>
        </div>
      </div>

      {/* Help Section */}
      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-2">
          Welcome to Hospital Management System
        </h3>
        <p className="text-blue-800 mb-4">
          Use the navigation menu to manage appointments, view medical records, and interact with healthcare professionals.
        </p>
        <div className="text-sm text-blue-700 space-y-1">
          <p>• View your appointments and upcoming schedules</p>
          <p>• Access your medical records and history</p>
          <p>• Find and connect with doctors</p>
          <p>• Manage your profile and account settings</p>
        </div>
      </div>
    </div>
  );
}
