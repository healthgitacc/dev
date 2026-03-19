'use client';

import { useEffect, useMemo, useState } from 'react';

import LoadingSpinner from '@/components/common/LoadingSpinner';
import apiClient from '@/lib/api';
import { useAuthStore } from '@/lib/auth-store';
import { API_ENDPOINTS } from '@/lib/constants';

type ReminderItem = {
  appointment_id: number;
  patient_id: number;
  patient_name: string;
  patient_phone: string | null;
  doctor_id: number;
  doctor_name: string;
  hospital_name: string | null;
  appointment_date: string;
  appointment_status: string;
  reminder_status: string;
  message_id: string | null;
  sent_at: string | null;
  responded_at: string | null;
  response_text: string | null;
};

const STATUS_OPTIONS = [
  { value: '', label: 'All statuses' },
  { value: 'pending', label: 'Pending' },
  { value: 'sent', label: 'Sent' },
  { value: 'yes', label: 'Yes' },
  { value: 'no', label: 'No' },
  { value: 'no_response', label: 'No-Response' },
  { value: 'failed', label: 'Failed' },
];

const statusClasses: Record<string, string> = {
  pending: 'bg-slate-100 text-slate-700',
  sent: 'bg-blue-100 text-blue-700',
  yes: 'bg-green-100 text-green-700',
  no: 'bg-red-100 text-red-700',
  no_response: 'bg-amber-100 text-amber-700',
  failed: 'bg-rose-100 text-rose-700',
};

export default function PatientRemindersPage() {
  const { user } = useAuthStore();
  const [items, setItems] = useState<ReminderItem[]>([]);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [daysAhead, setDaysAhead] = useState('7');
  const [search, setSearch] = useState('');

  const fetchReminders = async () => {
    try {
      setLoading(true);
      const params: Record<string, string | number> = {
        limit: 100,
        days_ahead: Number(daysAhead),
      };
      if (statusFilter) params.status = statusFilter;
      const response = await apiClient.get(API_ENDPOINTS.PATIENT_REMINDERS, { params });
      setItems(response.data?.items || []);
      setError('');
    } catch (err: any) {
      setError(err.response?.data?.detail?.message || err.message || 'Failed to load reminders');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user?.role !== 'hospital_admin') return;
    fetchReminders();
    const interval = window.setInterval(fetchReminders, 30000);
    return () => window.clearInterval(interval);
  }, [user?.role, statusFilter, daysAhead]);

  const visibleItems = useMemo(() => {
    const query = search.trim().toLowerCase();
    if (!query) return items;
    return items.filter((item) =>
      item.patient_name.toLowerCase().includes(query) ||
      item.doctor_name.toLowerCase().includes(query) ||
      (item.patient_phone || '').toLowerCase().includes(query)
    );
  }, [items, search]);

  const toggleSelected = (appointmentId: number) => {
    setSelectedIds((prev) =>
      prev.includes(appointmentId) ? prev.filter((id) => id !== appointmentId) : [...prev, appointmentId]
    );
  };

  const toggleSelectAllVisible = () => {
    const visibleIds = visibleItems.map((item) => item.appointment_id);
    const allVisibleSelected = visibleIds.length > 0 && visibleIds.every((id) => selectedIds.includes(id));
    if (allVisibleSelected) {
      setSelectedIds((prev) => prev.filter((id) => !visibleIds.includes(id)));
      return;
    }
    setSelectedIds((prev) => Array.from(new Set([...prev, ...visibleIds])));
  };

  const sendSelectedReminders = async () => {
    if (selectedIds.length === 0) {
      setError('Select at least one patient reminder to send.');
      return;
    }

    try {
      setSending(true);
      const response = await apiClient.post(API_ENDPOINTS.SEND_PATIENT_REMINDERS, {
        appointment_ids: selectedIds,
      });
      setMessage(`Sent: ${response.data.sent}, Failed: ${response.data.failed}`);
      setSelectedIds([]);
      await fetchReminders();
    } catch (err: any) {
      setError(err.response?.data?.detail?.message || err.message || 'Failed to send reminders');
    } finally {
      setSending(false);
    }
  };

  const formatDate = (value: string | null) => {
    if (!value) return 'Not sent yet';
    return new Date(value).toLocaleString();
  };

  if (user?.role !== 'hospital_admin') {
    return (
      <div className="py-12 text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Access Denied</h2>
        <p className="text-gray-600">Only hospital admins can manage patient reminders.</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="text-center py-12">
        <LoadingSpinner size="lg" text="Loading patient reminders..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Patient Reminders</h1>
          <p className="mt-2 text-gray-600">
            View upcoming appointments, send reminder SMS, and track YES/NO patient replies.
          </p>
        </div>
        <button
          type="button"
          onClick={sendSelectedReminders}
          disabled={sending || selectedIds.length === 0}
          className="rounded-lg bg-primary-600 px-5 py-3 text-white font-medium hover:bg-primary-700 disabled:opacity-50"
        >
          {sending ? 'Sending...' : `Send Reminder${selectedIds.length ? ` (${selectedIds.length})` : ''}`}
        </button>
      </div>

      {error && <div className="rounded-lg bg-red-50 border border-red-200 p-4 text-red-700">{error}</div>}
      {message && <div className="rounded-lg bg-green-50 border border-green-200 p-4 text-green-700">{message}</div>}

      <div className="grid grid-cols-1 gap-4 rounded-xl border border-slate-200 bg-white p-4 lg:grid-cols-4">
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search patient, phone, or doctor"
          className="rounded-lg border border-slate-300 px-3 py-2"
        />
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="rounded-lg border border-slate-300 px-3 py-2"
        >
          {STATUS_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        <select
          value={daysAhead}
          onChange={(e) => setDaysAhead(e.target.value)}
          className="rounded-lg border border-slate-300 px-3 py-2"
        >
          <option value="3">Next 3 days</option>
          <option value="7">Next 7 days</option>
          <option value="14">Next 14 days</option>
          <option value="30">Next 30 days</option>
        </select>
        <button
          type="button"
          onClick={() => {
            setSearch('');
            setStatusFilter('');
            setDaysAhead('7');
            setSelectedIds([]);
          }}
          className="rounded-lg border border-slate-300 px-3 py-2 text-slate-700 hover:bg-slate-50"
        >
          Reset Filters
        </button>
      </div>

      <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
        <table className="min-w-full text-sm">
          <thead className="bg-slate-50 text-left text-slate-600">
            <tr>
              <th className="px-4 py-3">
                <input
                  type="checkbox"
                  checked={visibleItems.length > 0 && visibleItems.every((item) => selectedIds.includes(item.appointment_id))}
                  onChange={toggleSelectAllVisible}
                />
              </th>
              <th className="px-4 py-3 font-semibold">Patient</th>
              <th className="px-4 py-3 font-semibold">Doctor</th>
              <th className="px-4 py-3 font-semibold">Appointment</th>
              <th className="px-4 py-3 font-semibold">Hospital</th>
              <th className="px-4 py-3 font-semibold">Status</th>
              <th className="px-4 py-3 font-semibold">Reply</th>
              <th className="px-4 py-3 font-semibold">Sent</th>
            </tr>
          </thead>
          <tbody>
            {visibleItems.map((item) => (
              <tr key={item.appointment_id} className="border-t border-slate-100">
                <td className="px-4 py-3">
                  <input
                    type="checkbox"
                    checked={selectedIds.includes(item.appointment_id)}
                    onChange={() => toggleSelected(item.appointment_id)}
                  />
                </td>
                <td className="px-4 py-3">
                  <div className="font-medium text-slate-900">{item.patient_name}</div>
                  <div className="text-slate-500">{item.patient_phone || 'No phone'}</div>
                </td>
                <td className="px-4 py-3 text-slate-700">{item.doctor_name}</td>
                <td className="px-4 py-3 text-slate-700">{formatDate(item.appointment_date)}</td>
                <td className="px-4 py-3 text-slate-700">{item.hospital_name || '-'}</td>
                <td className="px-4 py-3">
                  <span className={`rounded-full px-3 py-1 text-xs font-semibold ${statusClasses[item.reminder_status] || 'bg-slate-100 text-slate-700'}`}>
                    {item.reminder_status.replace('_', ' ')}
                  </span>
                </td>
                <td className="px-4 py-3 text-slate-700">{item.response_text || '-'}</td>
                <td className="px-4 py-3 text-slate-500">{formatDate(item.sent_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {visibleItems.length === 0 && (
          <div className="p-10 text-center text-slate-500">No reminder rows match the current filters.</div>
        )}
      </div>
    </div>
  );
}
