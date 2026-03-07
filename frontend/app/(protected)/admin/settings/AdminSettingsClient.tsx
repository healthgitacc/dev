'use client';

import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/auth-store';

export default function AdminSettingsClient() {
  const { user } = useAuthStore();
  const router = useRouter();

  // Redirect non-admins to dashboard
  if (!user || (user.role !== 'hospital_admin' && user.role !== 'super_admin')) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Access Denied</h2>
        <p className="text-gray-600">You don't have permission to access this page.</p>
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Admin Settings</h1>
        <div className="flex gap-3">
          <button
            onClick={() => router.push('/admin/add-doctor')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
          >
            Add Doctor
          </button>
          <button
            onClick={() => router.push('/admin/change-password')}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm"
          >
            Change Password
          </button>
        </div>
      </div>
      
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white rounded-lg shadow-sm p-6 mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">Welcome, {user.name}</h2>
            <p className="text-blue-100 mt-1">
              Role: {user.role === 'hospital_admin' ? 'Hospital Administrator' : 'Super Administrator'}
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm text-blue-100">Email: {user.email}</p>
            <p className="text-sm text-blue-100 mt-1">Phone: {user.phone || 'Not provided'}</p>
          </div>
        </div>
      </div>

      {/* Admin Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
        {/* Add Doctor */}
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200 hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">👨‍⚕️ Manage Doctors</h3>
            <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium">
              Admin Only
            </span>
          </div>
          <p className="text-gray-600 text-sm mb-4">
            Add new doctors to the hospital system and manage their profiles.
          </p>
          <button
            onClick={() => router.push('/admin/add-doctor')}
            className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            Add New Doctor
          </button>
        </div>

        {/* Change Password */}
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200 hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">🔒 Security</h3>
            <span className="px-2 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
              All Users
            </span>
          </div>
          <p className="text-gray-600 text-sm mb-4">
            Change your account password to keep your account secure.
          </p>
          <button
            onClick={() => router.push('/admin/change-password')}
            className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
          >
            Change Password
          </button>
        </div>

        {/* View Doctors */}
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200 hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">📋 Doctor Directory</h3>
            <span className="px-2 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-medium">
              View Only
            </span>
          </div>
          <p className="text-gray-600 text-sm mb-4">
            View and manage all doctor profiles in the hospital system.
          </p>
          <button
            onClick={() => router.push('/doctors')}
            className="w-full px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-medium"
          >
            View Doctors
          </button>
        </div>
      </div>

      {/* System Information */}
      <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">System Information</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-blue-50 rounded-lg p-4">
            <h3 className="font-medium text-blue-900 text-sm">Database</h3>
            <p className="text-blue-700 text-xs mt-1">Connected</p>
          </div>
          <div className="bg-green-50 rounded-lg p-4">
            <h3 className="font-medium text-green-900 text-sm">API Server</h3>
            <p className="text-green-700 text-xs mt-1">Running</p>
          </div>
          <div className="bg-yellow-50 rounded-lg p-4">
            <h3 className="font-medium text-yellow-900 text-sm">Notifications</h3>
            <p className="text-yellow-700 text-xs mt-1">Configured</p>
          </div>
          <div className="bg-purple-50 rounded-lg p-4">
            <h3 className="font-medium text-purple-900 text-sm">Auth System</h3>
            <p className="text-purple-700 text-xs mt-1">Active</p>
          </div>
        </div>
      </div>

      {/* Admin Notes */}
      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-3">📋 Admin Notes</h3>
        <div className="space-y-2 text-sm text-blue-800">
          <p>• Hospital admins can add and manage doctors</p>
          <p>• All doctor registrations include SMS notifications</p>
          <p>• Password changes are logged for security</p>
          <p>• System status is monitored automatically</p>
        </div>
      </div>
    </div>
  );
}