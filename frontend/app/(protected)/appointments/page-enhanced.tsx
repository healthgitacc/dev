'use client';

import { useState, useEffect } from 'react';
import apiClient from '@/lib/api';
import Link from 'next/link';

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
      const response = await apiClient.post(`/api/appointments/${appointment.id}/cancel`);
      setActionMessage('Appointment cancelled successfully and SMS sent to patient!');
      setTimeout(() => {
        setConfirmModal({ isOpen: false, action: null });
        setActionMessage('');
        onActionSuccess();
        onClose();
      }, 2000);
    } catch (error: any) {
      setActionMessage(
        error.response?.data?.detail || 'Failed to cancel appointment'
      );
    } finally {
      setActionLoading(false);
    }
  };

  const handleCompleteAppointment = async () => {
    setActionLoading(true);
    try {
      const response = await apiClient.post(`/api/appointments/${appointment.id}/complete`);
      setActionMessage('Appointment marked as completed!');
      setTimeout(() => {
        setConfirmModal({ isOpen: false, action: null });
        setActionMessage('');
        onActionSuccess();
        onClose();
      }, 2000);
    } catch (error: any) {
      setActionMessage(
        error.response?.data?.detail || 'Failed to complete appointment'
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
                  <button
                    onClick={() => setConfirmModal({ isOpen: true, action: 'complete' })}
                    disabled={actionLoading}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium disabled:opacity-50"
                  >
                    ✓ Mark Complete
                  </button>
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
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [filteredAppointments, setFilteredAppointments] = useState<Appointment[]>([]);
  const [statusFilter, setStatusFilter] = useState('All');
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

  // Filter by status
  useEffect(() => {
    if (statusFilter === 'All') {
      setFilteredAppointments(appointments);
    } else {
      setFilteredAppointments(
        appointments.filter((apt) => apt.status === statusFilter)
      );
    }
  }, [statusFilter, appointments]);

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
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <p className="mt-4 text-gray-600">Loading appointments...</p>
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

      {/* Status Filter */}
      <div className="mb-6 bg-white rounded-lg shadow-sm p-4 border border-gray-200">
        <div className="flex gap-2 flex-wrap">
          {['All', 'scheduled', 'completed', 'cancelled'].map((status) => (
            <button
              key={status}
              onClick={() => setStatusFilter(status)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                statusFilter === status
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </button>
          ))}
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
