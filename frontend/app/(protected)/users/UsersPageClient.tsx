'use client';

import { useEffect, useState, useCallback } from 'react';
import { useAuthStore } from '@/lib/auth-store';
import { apiClient } from '@/lib/api';
import { API_ENDPOINTS } from '@/lib/constants';
import { ROLE_LABELS, ROLE_COLORS } from '@/lib/constants';

interface UserRow {
  id: number;
  name: string;
  email: string;
  phone: string | null;
  role: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

const ROLE_OPTIONS: { value: string; label: string }[] = [
  { value: '', label: 'All Roles' },
  { value: 'super_admin', label: 'Admin' },
  { value: 'doctor', label: 'Doctor' },
  { value: 'patient', label: 'Patient' },
  { value: 'hospital_admin', label: 'Hospital Admin' },
  { value: 'super_owner', label: 'Super Owner' },
];

export function UsersPageClient() {
  const { user } = useAuthStore();
  const [users, setUsers] = useState<UserRow[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchInput, setSearchInput] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [includeInactive, setIncludeInactive] = useState(false);
  const [actioningId, setActioningId] = useState<number | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const isHospitalAdmin = user?.role === 'hospital_admin';
  const canEdit = !isHospitalAdmin; // hospital_admin: view only (email, phone, status)
  // Hospital admin can activate, deactivate, remove only doctor and patient users
  const canManageDoctorPatient = isHospitalAdmin;
  const isDoctorOrPatient = (role: string) => role === 'doctor' || role === 'patient';

  const fetchUsers = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      let items: UserRow[] = [];
      const q = searchQuery.trim();
      const hasSearch = q.length >= 2;

      const commonParams = { skip: 0, limit: 100, include_inactive: includeInactive };
      if (roleFilter) {
        const res = await apiClient.get<{ items: UserRow[]; total: number }>(
          `${API_ENDPOINTS.USERS}/search/by-role/${encodeURIComponent(roleFilter)}`,
          { params: commonParams }
        );
        items = res.data?.items ?? [];
      } else if (hasSearch) {
        const res = await apiClient.get<{ items: UserRow[]; total: number }>(
          `${API_ENDPOINTS.USERS}/search/query`,
          { params: { ...commonParams, q } }
        );
        items = res.data?.items ?? [];
      } else {
        const res = await apiClient.get<{ items: UserRow[]; total: number }>(
          `${API_ENDPOINTS.USERS}`,
          { params: commonParams }
        );
        items = res.data?.items ?? [];
      }

      if (hasSearch && items.length > 0) {
        const lower = q.toLowerCase();
        items = items.filter(
          (u) =>
            (u.name && u.name.toLowerCase().includes(lower)) ||
            (u.email && u.email.toLowerCase().includes(lower)) ||
            (u.phone && u.phone.includes(q))
        );
      }

      setUsers(items);
      setTotal(items.length);
    } catch (e: unknown) {
      const message = e && typeof e === 'object' && 'response' in e
        ? (e as { response?: { data?: { detail?: string } } }).response?.data?.detail
        : 'Failed to load users';
      setError(typeof message === 'string' ? message : 'Failed to load users');
      setUsers([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, [searchQuery, roleFilter, includeInactive]);

  useEffect(() => {
    let cancelled = false;
    const run = async () => {
      await fetchUsers();
      if (cancelled) return;
    };
    run();
    return () => { cancelled = true; };
  }, [fetchUsers]);

  useEffect(() => {
    const t = setTimeout(() => setSearchQuery(searchInput), 350);
    return () => clearTimeout(t);
  }, [searchInput]);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchInput(e.target.value);
  };

  const handleRoleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setRoleFilter(e.target.value);
  };

  const handleActivate = async (userId: number) => {
    if (actioningId != null) return;
    setActioningId(userId);
    setSuccessMessage(null);
    try {
      await apiClient.post(API_ENDPOINTS.USER_ACTIVATE(userId));
      setError(null);
      setSuccessMessage('User activated successfully.');
      await fetchUsers();
    } catch (e: unknown) {
      const msg = e && typeof e === 'object' && 'response' in e
        ? (e as { response?: { data?: { detail?: string } } }).response?.data?.detail
        : 'Failed to activate user';
      setError(typeof msg === 'string' ? msg : 'Failed to activate user');
    } finally {
      setActioningId(null);
    }
  };

  const handleDeactivate = async (userId: number) => {
    if (actioningId != null) return;
    setActioningId(userId);
    setSuccessMessage(null);
    try {
      await apiClient.post(API_ENDPOINTS.USER_DEACTIVATE(userId));
      setError(null);
      setSuccessMessage('User deactivated successfully.');
      await fetchUsers();
    } catch (e: unknown) {
      const msg = e && typeof e === 'object' && 'response' in e
        ? (e as { response?: { data?: { detail?: string } } }).response?.data?.detail
        : 'Failed to deactivate user';
      setError(typeof msg === 'string' ? msg : 'Failed to deactivate user');
    } finally {
      setActioningId(null);
    }
  };

  const handleRemove = async (userId: number) => {
    if (actioningId != null) return;
    if (!confirm('Are you sure you want to remove this user? This cannot be undone.')) return;
    setActioningId(userId);
    setSuccessMessage(null);
    try {
      await apiClient.delete(API_ENDPOINTS.USER_BY_ID(userId));
      setError(null);
      setSuccessMessage('User removed successfully.');
      await fetchUsers();
    } catch (e: unknown) {
      const msg = e && typeof e === 'object' && 'response' in e
        ? (e as { response?: { data?: { detail?: string } } }).response?.data?.detail
        : 'Failed to remove user';
      setError(typeof msg === 'string' ? msg : 'Failed to remove user');
    } finally {
      setActioningId(null);
    }
  };

  const roleLabel = (role: string) => ROLE_LABELS[role] ?? role?.replace('_', ' ') ?? '—';
  const roleColor = (role: string) => ROLE_COLORS[role] ?? 'bg-gray-100 text-gray-800';

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Users</h1>

      {/* Search and Filter - hide Add User for hospital_admin */}
      <div className="mb-6 bg-white rounded-lg shadow-sm p-6 border border-gray-200">
        <div className="flex gap-4">
          <input
            type="text"
            placeholder="Search users (name, email, phone)..."
            value={searchInput}
            onChange={handleSearchChange}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent"
          />
          <select
            value={roleFilter}
            onChange={handleRoleChange}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent"
          >
            {ROLE_OPTIONS.map((opt) => (
              <option key={opt.value || 'all'} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          {canManageDoctorPatient && (
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={includeInactive}
                onChange={(e) => setIncludeInactive(e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-600"
              />
              <span className="text-sm text-gray-700">Include inactive (to activate)</span>
            </label>
          )}
          {canEdit && (
            <button
              type="button"
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              Add User
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="mb-6 rounded-lg bg-red-50 border border-red-200 p-4">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}
      {successMessage && (
        <div className="mb-6 rounded-lg bg-green-50 border border-green-200 p-4">
          <p className="text-sm text-green-700">{successMessage}</p>
        </div>
      )}

      {/* Users Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Name</th>
              <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Email</th>
              <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Phone</th>
              <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Role</th>
              <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Status</th>
              <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {loading ? (
              <tr>
                <td colSpan={6} className="px-6 py-8 text-center text-gray-500">
                  Loading users...
                </td>
              </tr>
            ) : users.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-6 py-8 text-center text-gray-500">
                  No users found.
                </td>
              </tr>
            ) : (
              users.map((u) => (
                <tr key={u.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm text-gray-900">{u.name || '—'}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{u.email}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{u.phone || '—'}</td>
                  <td className="px-6 py-4 text-sm">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${roleColor(u.role)}`}>
                      {roleLabel(u.role)}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm">
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium ${
                        u.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {u.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm space-x-2">
                    <button type="button" className="text-blue-600 hover:text-blue-700">
                      View
                    </button>
                    {canEdit && (
                      <button type="button" className="text-gray-600 hover:text-gray-700">
                        Edit
                      </button>
                    )}
                    {canManageDoctorPatient && isDoctorOrPatient(u.role) && (
                      <>
                        {u.is_active ? (
                          <button
                            type="button"
                            onClick={() => handleDeactivate(u.id)}
                            disabled={actioningId === u.id}
                            className="text-amber-600 hover:text-amber-700 disabled:opacity-50"
                          >
                            {actioningId === u.id ? '…' : 'Deactivate'}
                          </button>
                        ) : (
                          <button
                            type="button"
                            onClick={() => handleActivate(u.id)}
                            disabled={actioningId === u.id}
                            className="text-green-600 hover:text-green-700 disabled:opacity-50"
                          >
                            {actioningId === u.id ? '…' : 'Activate'}
                          </button>
                        )}
                        <button
                          type="button"
                          onClick={() => handleRemove(u.id)}
                          disabled={actioningId === u.id}
                          className="text-red-600 hover:text-red-700 disabled:opacity-50"
                        >
                          {actioningId === u.id ? '…' : 'Remove'}
                        </button>
                      </>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      {!loading && total > 0 && (
        <p className="mt-2 text-sm text-gray-500">Total: {total} user(s)</p>
      )}
    </div>
  );
}
