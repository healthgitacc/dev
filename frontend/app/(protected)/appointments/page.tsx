'use client';

import { useState, useEffect } from 'react';
import apiClient from '@/lib/api';
import Link from 'next/link';
import { useAuthStore } from '@/lib/auth-store';
import LoadingSpinner from '@/components/common/LoadingSpinner';

interface Appointment {
  id: number;
  doctor_id: number;
  doctor_name: string;
  doctor_specialization: string;
  patient_id: number;
  patient_name: string;
  patient_email: string;
  appointment_date: string;
  duration_minutes: number;
  notes: string;
  status: string;
  reminder_sent: string | null;
  created_at: string;
  updated_at: string;
}

interface DetailModalProps {
  appointment: Appointment | null;
  isOpen: boolean;
  onClose: () => void;
  onActionSuccess: () => void;
}

// Confirmation Modal
function ConfirmationModal({
  isOpen,
  title,
  message,
  onConfirm,
  onCancel,
  isLoading,
  isDangerous,
}: {
  isOpen: boolean;
  title: string;
  message: string;
  onConfirm: () => Promise<void>;
  onCancel: () => void;
  isLoading: boolean;
  isDangerous?: boolean;
}) {
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleConfirm = async () => {
    setLoading(true);
    try {
      await onConfirm();
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-[60] flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-lg max-w-md w-full">
        <div className="p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-2">{title}</h2>
          <p className="text-gray-600 mb-6">{message}</p>
          <div className="flex gap-3 justify-end">
            <button
              onClick={onCancel}
              disabled={loading}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              onClick={handleConfirm}
              disabled={loading}
              className={`px-4 py-2 text-white rounded-lg hover:opacity-90 transition-colors font-medium disabled:opacity-50 ${
                isDangerous
                  ? 'bg-red-600 hover:bg-red-700'
                  : 'bg-blue-600 hover:bg-blue-700'
              }`}
            >
              {loading ? 'Processing...' : 'Confirm'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// Appointment Details Modal
function AppointmentDetailModal({ appointment, isOpen, onClose, onActionSuccess }: DetailModalProps) {
  const { user } = useAuthStore();
  const [confirmModal, setConfirmModal] = useState<{
    isOpen: boolean;
    action: 'cancel' | 'complete' | null;
  }>({ isOpen: false, action: null });
  const [actionLoading, setActionLoading] = useState(false);
  const [actionMessage, setActionMessage] = useState('');

  if (!isOpen || !appointment) return null;

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return dateString;
    }
  };

  const handleCancelAppointment = async () => {
    setActionLoading(true);
    try {
      await apiClient.post(`/api/appointments/${appointment.id}/cancel`);
      setActionMessage('Appointment cancelled successfully and SMS sent to patient!');
      setTimeout(() => {
        setConfirmModal({ isOpen: false, action: null });
        setActionMessage('');
        onActionSuccess();
        onClose();
      }, 1500);
    } catch (error: any) {
      console.error('Cancel error:', error.response?.data);
      setActionMessage(
        error.response?.data?.detail || error.message || 'Failed to cancel appointment'
      );
    } finally {
      setActionLoading(false);
    }
  };

  const handleCompleteAppointment = async () => {
    setActionLoading(true);
    try {
      await apiClient.post(`/api/appointments/${appointment.id}/complete`);
      setActionMessage('Appointment marked as completed!');
      setTimeout(() => {
        setConfirmModal({ isOpen: false, action: null });
        setActionMessage('');
        onActionSuccess();
        onClose();
      }, 1500);
    } catch (error: any) {
      console.error('Complete error:', error.response?.data);
      setActionMessage(
        error.response?.data?.detail || error.message || 'Failed to complete appointment'
      );
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <>
      <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
          <div className="sticky top-0 bg-white border-b border-gray-200 p-6 flex justify-between items-center">
            <h2 className="text-2xl font-bold text-gray-900">Appointment Details</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 font-bold text-2xl"
            >
              ×
            </button>
          </div>

          <div className="p-6 space-y-6">
            {/* Doctor Information */}
            <div className="border-b border-gray-200 pb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">👨‍⚕️ Doctor Information</h3>
              <div className="bg-blue-50 rounded-lg p-4 space-y-2">
                <p>
                  <span className="font-medium text-gray-700">Name:</span>{' '}
                  <span className="text-gray-900">{appointment.doctor_name}</span>
                </p>
                <p>
                  <span className="font-medium text-gray-700">Specialization:</span>{' '}
                  <span className="text-gray-900">{appointment.doctor_specialization}</span>
                </p>
              </div>
            </div>

            {/* Patient Information */}
            <div className="border-b border-gray-200 pb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">👤 Patient Information</h3>
              <div className="bg-green-50 rounded-lg p-4 space-y-2">
                <p>
                  <span className="font-medium text-gray-700">Name:</span>{' '}
                  <span className="text-gray-900">{appointment.patient_name}</span>
                </p>
                <p>
                  <span className="font-medium text-gray-700">Email:</span>{' '}
                  <span className="text-gray-900">{appointment.patient_email}</span>
                </p>
              </div>
            </div>

            {/* Appointment Details */}
            <div className="border-b border-gray-200 pb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">📅 Appointment Details</h3>
              <div className="space-y-3">
                <p>
                  <span className="font-medium text-gray-700">Date & Time:</span>{' '}
                  <span className="text-gray-900">{formatDate(appointment.appointment_date)}</span>
                </p>
                <p>
                  <span className="font-medium text-gray-700">Duration:</span>{' '}
                  <span className="text-gray-900">{appointment.duration_minutes} minutes</span>
                </p>
                <p>
                  <span className="font-medium text-gray-700">Status:</span>{' '}
                  <span
                    className={`px-3 py-1 rounded-full text-sm font-medium ${
                      appointment.status === 'scheduled'
                        ? 'bg-blue-100 text-blue-700'
                        : appointment.status === 'completed'
                        ? 'bg-green-100 text-green-700'
                        : 'bg-red-100 text-red-700'
                    }`}
                  >
                    {appointment.status.charAt(0).toUpperCase() + appointment.status.slice(1)}
                  </span>
                </p>
              </div>
            </div>

            {/* Notes */}
            {appointment.notes && (
              <div className="border-b border-gray-200 pb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">📝 Notes</h3>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-gray-700">{appointment.notes}</p>
                </div>
              </div>
            )}

            {/* Action Message */}
            {actionMessage && (
              <div
                className={`p-4 rounded-lg ${
                  actionMessage.includes('successfully')
                    ? 'bg-green-100 text-green-700'
                    : 'bg-red-100 text-red-700'
                }`}
              >
                {actionMessage}
              </div>
            )}

            {/* Timestamps */}
            <div className="text-xs text-gray-500 space-y-1">
              <p>Created: {formatDate(appointment.created_at)}</p>
              <p>Updated: {formatDate(appointment.updated_at)}</p>
            </div>

            {/* Actions */}
            <div className="flex gap-2 justify-end pt-4 flex-wrap">
              {appointment.status === 'scheduled' && (
                <>
                  {(user?.role === 'doctor' || user?.role === 'admin' || user?.role === 'hospital_admin' || user?.role === 'super_admin') && (
                    <button
                      onClick={() => setConfirmModal({ isOpen: true, action: 'complete' })}
                      disabled={actionLoading}
                      className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium disabled:opacity-50"
                      title="Only doctors and admins can mark appointments as complete"
                    >
                      ✓ Mark Complete
                    </button>
                  )}
                  <button
                    onClick={() => setConfirmModal({ isOpen: true, action: 'cancel' })}
                    disabled={actionLoading}
                    className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium disabled:opacity-50"
                  >
                    Cancel Appointment
                  </button>
                </>
              )}
              <button
                onClick={onClose}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      </div>

      <ConfirmationModal
        isOpen={confirmModal.isOpen}
        title={confirmModal.action === 'cancel' ? 'Cancel Appointment' : 'Complete Appointment'}
        message={
          confirmModal.action === 'cancel'
            ? 'Are you sure you want to cancel this appointment? An SMS notification will be sent to the patient.'
            : 'Mark this appointment as completed?'
        }
        onConfirm={
          confirmModal.action === 'cancel'
            ? handleCancelAppointment
            : handleCompleteAppointment
        }
        onCancel={() => setConfirmModal({ isOpen: false, action: null })}
        isLoading={actionLoading}
        isDangerous={confirmModal.action === 'cancel'}
      />
    </>
  );
}

export default function AppointmentsPage() {
  const { user } = useAuthStore();
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [filteredAppointments, setFilteredAppointments] = useState<Appointment[]>([]);
  const [statusFilter, setStatusFilter] = useState('All');
  const [doctorFilter, setDoctorFilter] = useState('');
  const [patientNameFilter, setPatientNameFilter] = useState('');
  const [patientEmailFilter, setPatientEmailFilter] = useState('');
  const [dateFilter, setDateFilter] = useState('');
  const [sortBy, setSortBy] = useState('date_desc');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedAppointment, setSelectedAppointment] = useState<Appointment | null>(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);

  // Fetch appointments
  const fetchAppointments = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/api/appointments');
      const appointmentsList = response.data.items || [];
      setAppointments(appointmentsList);
      setFilteredAppointments(appointmentsList);
      setError('');
    } catch (err) {
      setError('Failed to load appointments');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAppointments();
  }, []);

  // Filter and sort appointments
  useEffect(() => {
    let filtered = appointments;

    // Filter by status
    if (statusFilter !== 'All') {
      filtered = filtered.filter((apt) => apt.status === statusFilter);
    }

    // Filter by doctor name
    if (doctorFilter.trim()) {
      filtered = filtered.filter((apt) =>
        apt.doctor_name.toLowerCase().includes(doctorFilter.toLowerCase())
      );
    }

    // Filter by patient name
    if (patientNameFilter.trim()) {
      filtered = filtered.filter((apt) =>
        apt.patient_name.toLowerCase().includes(patientNameFilter.toLowerCase())
      );
    }

    // Filter by patient email
    if (patientEmailFilter.trim()) {
      filtered = filtered.filter((apt) =>
        apt.patient_email.toLowerCase().includes(patientEmailFilter.toLowerCase())
      );
    }

    // Filter by date
    if (dateFilter) {
      filtered = filtered.filter((apt) => {
        const aptDate = new Date(apt.appointment_date).toDateString();
        const filterDate = new Date(dateFilter).toDateString();
        return aptDate === filterDate;
      });
    }

    // Sort appointments
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'date_asc':
          return new Date(a.appointment_date).getTime() - new Date(b.appointment_date).getTime();
        case 'date_desc':
          return new Date(b.appointment_date).getTime() - new Date(a.appointment_date).getTime();
        case 'doctor_name':
          return a.doctor_name.localeCompare(b.doctor_name);
        case 'patient_name':
          return a.patient_name.localeCompare(b.patient_name);
        default:
          return 0;
      }
    });

    setFilteredAppointments(filtered);
  }, [statusFilter, doctorFilter, patientNameFilter, patientEmailFilter, dateFilter, sortBy, appointments]);

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return dateString;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'scheduled':
        return 'bg-blue-100 text-blue-700';
      case 'completed':
        return 'bg-green-100 text-green-700';
      case 'cancelled':
        return 'bg-red-100 text-red-700';
      default:
        return 'bg-gray-100 text-gray-700';
    }
  };

  if (loading) {
    return (
      <div className="text-center py-12">
        <LoadingSpinner size="lg" text="Loading appointments..." />
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Appointments</h1>
        <Link href="/book-appointment">
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm">
            Book New Appointment
          </button>
        </Link>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-100 text-red-700 rounded-lg">
          {error}
        </div>
      )}

      {/* Advanced Filters */}
      <div className="mb-6 bg-white rounded-lg shadow-sm p-6 border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">🔍 Advanced Filters</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {/* Status Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent"
            >
              <option value="All">All Statuses</option>
              <option value="scheduled">Scheduled</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>

          {/* Doctor Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Doctor</label>
            <input
              type="text"
              placeholder="Search doctor name..."
              value={doctorFilter}
              onChange={(e) => setDoctorFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent"
            />
          </div>

          {/* Patient Name Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Patient Name</label>
            <input
              type="text"
              placeholder="Search patient name..."
              value={patientNameFilter}
              onChange={(e) => setPatientNameFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent"
            />
          </div>

          {/* Patient Email Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Patient Email</label>
            <input
              type="text"
              placeholder="Search patient email..."
              value={patientEmailFilter}
              onChange={(e) => setPatientEmailFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent"
            />
          </div>

          {/* Date Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Date</label>
            <input
              type="date"
              value={dateFilter}
              onChange={(e) => setDateFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent"
            />
          </div>
        </div>

        {/* Sort Options */}
        <div className="mt-4 flex flex-wrap gap-4">
          <div className="flex items-center space-x-2">
            <label className="text-sm font-medium text-gray-700">Sort by:</label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent"
            >
              <option value="date_desc">Date (Newest)</option>
              <option value="date_asc">Date (Oldest)</option>
              <option value="doctor_name">Doctor Name</option>
              <option value="patient_name">Patient Name</option>
            </select>
          </div>

          <button
            onClick={() => {
              setStatusFilter('All');
              setDoctorFilter('');
              setPatientNameFilter('');
              setPatientEmailFilter('');
              setDateFilter('');
              setSortBy('date_desc');
            }}
            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
          >
            Clear Filters
          </button>
        </div>
      </div>

      {/* Appointments List */}
      {filteredAppointments.length > 0 ? (
        <div className="space-y-4">
          {filteredAppointments.map((appointment) => (
            <div
              key={appointment.id}
              className="bg-white rounded-lg shadow-sm p-6 border border-gray-200 hover:shadow-md transition-shadow"
            >
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">
                    {appointment.doctor_name || 'Dr. Unknown'}
                  </h3>
                  <p className="text-sm text-blue-600">
                    {appointment.doctor_specialization || 'N/A'}
                  </p>
                </div>
                <span
                  className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(
                    appointment.status
                  )}`}
                >
                  {appointment.status.charAt(0).toUpperCase() +
                    appointment.status.slice(1)}
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600 mb-4">
                <div>
                  <p className="font-medium text-gray-900">📅 Date & Time</p>
                  <p>{formatDate(appointment.appointment_date)}</p>
                </div>
                <div>
                  <p className="font-medium text-gray-900">⏱️ Duration</p>
                  <p>{appointment.duration_minutes} minutes</p>
                </div>
              </div>

              {appointment.notes && (
                <div className="mb-4 p-3 bg-gray-50 rounded-lg border border-gray-200">
                  <p className="text-xs font-medium text-gray-600">Notes</p>
                  <p className="text-sm text-gray-700">{appointment.notes}</p>
                </div>
              )}

              <div className="flex gap-2 flex-wrap">
                <button
                  onClick={() => {
                    setSelectedAppointment(appointment);
                    setIsDetailModalOpen(true);
                  }}
                  className="flex-1 min-w-[100px] px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium"
                >
                  View Details
                </button>
                {appointment.status === 'scheduled' && (
                  <>
                    <button
                      onClick={() => {
                        setSelectedAppointment(appointment);
                        setIsDetailModalOpen(true);
                      }}
                      className="flex-1 min-w-[100px] px-4 py-2 border border-green-300 text-green-700 rounded-lg hover:bg-green-50 transition-colors text-sm font-medium"
                    >
                      ✓ Complete
                    </button>
                    <button
                      onClick={() => {
                        setSelectedAppointment(appointment);
                        setIsDetailModalOpen(true);
                      }}
                      className="flex-1 min-w-[100px] px-4 py-2 border border-red-300 text-red-700 rounded-lg hover:bg-red-50 transition-colors text-sm font-medium"
                    >
                      Cancel
                    </button>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm p-12 text-center border border-gray-200">
          <div className="text-4xl mb-4">📅</div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            No appointments found
          </h2>
          <p className="text-gray-600 mb-6">
            {statusFilter === 'All'
              ? 'You have no appointments yet.'
              : `You have no ${statusFilter} appointments.`}
          </p>
          <Link href="/doctors">
            <button className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
              Book Appointment Now
            </button>
          </Link>
        </div>
      )}

      {/* Appointment Detail Modal */}
      <AppointmentDetailModal
        appointment={selectedAppointment}
        isOpen={isDetailModalOpen}
        onClose={() => {
          setIsDetailModalOpen(false);
          setSelectedAppointment(null);
        }}
        onActionSuccess={() => {
          fetchAppointments();
        }}
      />
    </div>
  );
}
