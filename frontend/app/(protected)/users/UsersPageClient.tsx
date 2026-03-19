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
  const roleColor = (role: string) => ROLE_COLORS[role] ?? 'bg-slate-100 text-slate-800';

  const ActionButtons = ({ u }: { u: UserRow }) => (
    <div className="flex flex-wrap gap-2">
      <button type="button" className="text-primary-600 hover:text-primary-700 text-sm font-medium">
        View
      </button>
      {canEdit && (
        <button type="button" className="text-slate-600 hover:text-slate-700 text-sm font-medium">
          Edit
        </button>
      )}
      {canManageDoctorPatient && isDoctorOrPatient(u.role) && (
        <>
          {u.is_active ? (
            <button type="button" onClick={() => handleDeactivate(u.id)} disabled={actioningId === u.id} className="text-amber-600 hover:text-amber-700 disabled:opacity-50 text-sm font-medium">
              {actioningId === u.id ? '…' : 'Deactivate'}
            </button>
          ) : (
            <button type="button" onClick={() => handleActivate(u.id)} disabled={actioningId === u.id} className="text-emerald-600 hover:text-emerald-700 disabled:opacity-50 text-sm font-medium">
              {actioningId === u.id ? '…' : 'Activate'}
            </button>
          )}
          <button type="button" onClick={() => handleRemove(u.id)} disabled={actioningId === u.id} className="text-red-600 hover:text-red-700 disabled:opacity-50 text-sm font-medium">
            {actioningId === u.id ? '…' : 'Remove'}
          </button>
        </>
      )}
    </div>
  );

  return (
    <div className="space-y-6">
      <h1 className="text-2xl sm:text-3xl font-bold text-slate-900">Users</h1>

      <div className="card p-4 sm:p-6">
        <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 flex-wrap">
          <input
            type="text"
            placeholder="Search (name, email, phone)..."
            value={searchInput}
            onChange={handleSearchChange}
            className="input-base flex-1 min-w-0 sm:min-w-[200px]"
          />
          <select value={roleFilter} onChange={handleRoleChange} className="input-base w-full sm:w-auto sm:min-w-[160px]">
            {ROLE_OPTIONS.map((opt) => (
              <option key={opt.value || 'all'} value={opt.value}>{opt.label}</option>
            ))}
          </select>
          {canManageDoctorPatient && (
            <label className="flex items-center gap-2 cursor-pointer shrink-0">
              <input type="checkbox" checked={includeInactive} onChange={(e) => setIncludeInactive(e.target.checked)} className="rounded border-slate-300 text-primary-600 focus:ring-primary-500" />
              <span className="text-sm text-slate-600">Include inactive</span>
            </label>
          )}
          {canEdit && <button type="button" className="btn-primary shrink-0">Add User</button>}
        </div>
      </div>

      {error && (
        <div className="rounded-xl bg-red-50 border border-red-200 p-4">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}
      {successMessage && (
        <div className="rounded-xl bg-emerald-50 border border-emerald-200 p-4">
          <p className="text-sm text-emerald-700">{successMessage}</p>
        </div>
      )}

      {/* Desktop: table */}
      <div className="card overflow-hidden hidden md:block">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[640px]">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Name</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Email</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Phone</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Role</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Status</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr><td colSpan={6} className="px-4 py-12 text-center text-slate-500">Loading users...</td></tr>
              ) : users.length === 0 ? (
                <tr><td colSpan={6} className="px-4 py-12 text-center text-slate-500">No users found.</td></tr>
              ) : (
                users.map((u) => (
                  <tr key={u.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="px-4 py-3 text-sm font-medium text-slate-900">{u.name || '—'}</td>
                    <td className="px-4 py-3 text-sm text-slate-600">{u.email}</td>
                    <td className="px-4 py-3 text-sm text-slate-600">{u.phone || '—'}</td>
                    <td className="px-4 py-3"><span className={`badge ${roleColor(u.role)}`}>{roleLabel(u.role)}</span></td>
                    <td className="px-4 py-3">
                      <span className={`badge ${u.is_active ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'}`}>
                        {u.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-4 py-3"><ActionButtons u={u} /></td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Mobile: cards */}
      <div className="md:hidden space-y-3">
        {loading ? (
          <div className="card p-8 text-center text-slate-500">Loading users...</div>
        ) : users.length === 0 ? (
          <div className="card p-8 text-center text-slate-500">No users found.</div>
        ) : (
          users.map((u) => (
            <div key={u.id} className="card p-4">
              <div className="flex justify-between items-start gap-2 mb-2">
                <p className="font-medium text-slate-900 truncate">{u.name || '—'}</p>
                <span className={`badge shrink-0 ${roleColor(u.role)}`}>{roleLabel(u.role)}</span>
              </div>
              <p className="text-sm text-slate-600 truncate">{u.email}</p>
              <p className="text-sm text-slate-500">{u.phone || '—'}</p>
              <div className="flex items-center gap-2 mt-3">
                <span className={`badge text-xs ${u.is_active ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'}`}>
                  {u.is_active ? 'Active' : 'Inactive'}
                </span>
                <ActionButtons u={u} />
              </div>
            </div>
          ))
        )}
      </div>

      {!loading && total > 0 && <p className="text-sm text-slate-500">Total: {total} user(s)</p>}
    </div>
  );
}
