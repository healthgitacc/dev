'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import apiClient from '@/lib/api';
import Link from 'next/link';
import { useAuthStore } from '@/lib/auth-store';

interface Doctor {
  id: number;
  name: string;
  specialization: string;
  experience_years: number;
}

interface Patient {
  id: number;
  user: {
    name: string;
    email: string;
    phone: string;
  };
  blood_group?: string;
  gender?: string;
}

export default function BookAppointmentPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user } = useAuthStore();
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  const preSelectedDoctorId = searchParams?.get('doctor_id') || '';
  const isHospitalAdmin = user?.role === 'admin' || user?.role === 'hospital_admin' || user?.role === 'super_admin';

  const [formData, setFormData] = useState({
    patient_id: '',
    doctor_id: preSelectedDoctorId,
    appointment_date: '',
    appointment_time: '',
    chief_complaint: '',
    symptoms: '',
    notes: '',
  });

  // Fetch doctors and patients (if admin)
  useEffect(() => {
    const fetchData = async () => {
      try {
        const doctorResponse = await apiClient.get('/api/doctors');
        setDoctors(doctorResponse.data.items || []);
        
        if (isHospitalAdmin) {
          const patientResponse = await apiClient.get('/api/admin/patients');
          setPatients(patientResponse.data.items || []);
        }
        
        setLoading(false);
      } catch (err) {
        console.error('Failed to load data:', err);
        setError('Failed to load required data');
        setLoading(false);
      }
    };

    fetchData();
  }, [isHospitalAdmin]);

  // Update form when pre-selected doctor changes
  useEffect(() => {
    if (preSelectedDoctorId) {
      setFormData((prev) => ({
        ...prev,
        doctor_id: preSelectedDoctorId,
      }));
    }
  }, [preSelectedDoctorId]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setFieldErrors({});

    // Validation
    const errors: Record<string, string> = {};
    if (!formData.doctor_id) errors.doctor_id = 'Doctor is required';
    if (!formData.appointment_date) errors.appointment_date = 'Date is required';
    if (!formData.appointment_time) errors.appointment_time = 'Time is required';
    
    // Check if time is within allowed range (09:00 - 16:59)
    if (formData.appointment_time && formData.appointment_time >= '17:00') {
      errors.appointment_time = 'Appointments only available between 09:00 AM - 04:59 PM';
    }

    if (Object.keys(errors).length > 0) {
      setFieldErrors(errors);
      setError('Please fix the errors before submitting');
      return;
    }

    setSubmitting(true);

    try {
      let appointmentData;
      let endpoint;

      if (isHospitalAdmin) {
        // Hospital admin booking appointment for patient
        if (!formData.patient_id) {
          setFieldErrors({ patient_id: 'Patient is required' });
          setError('Please select a patient before submitting');
          setSubmitting(false);
          return;
        }
        if (!formData.chief_complaint) {
          setFieldErrors({ chief_complaint: 'Chief complaint is required' });
          setError('Please enter the chief complaint');
          setSubmitting(false);
          return;
        }
        
        appointmentData = {
          patient_id: parseInt(formData.patient_id),
          doctor_id: parseInt(formData.doctor_id),
          appointment_date: `${formData.appointment_date}T${formData.appointment_time}:00Z`,
          duration_minutes: 30,
          chief_complaint: formData.chief_complaint,
          symptoms: formData.symptoms || '',
          notes: formData.notes || '',
        };
        endpoint = '/api/admin/appointments';
      } else {
        // Patient booking appointment for themselves
        appointmentData = {
          doctor_id: parseInt(formData.doctor_id),
          appointment_date: `${formData.appointment_date}T${formData.appointment_time}:00`,
          duration_minutes: 30,
          notes: formData.notes || 'No notes',
        };
        endpoint = '/api/appointments';
      }

      const response = await apiClient.post(endpoint, appointmentData);

      setSuccess('✅ Appointment booked successfully! Redirecting...');
      setFormData({
        patient_id: '',
        doctor_id: preSelectedDoctorId || '',
        appointment_date: '',
        appointment_time: '',
        chief_complaint: '',
        symptoms: '',
        notes: '',
      });
      setFieldErrors({});

      // Redirect to appointments page after 2 seconds
      setTimeout(() => {
        router.push('/appointments');
      }, 2000);
    } catch (err: any) {
      console.error('Booking error:', err);
      
      // Handle different error types
      let errorMessage = 'Failed to book appointment';
      const errors: Record<string, string> = {};
      
      if (err.response?.data?.detail) {
        if (typeof err.response.data.detail === 'string') {
          errorMessage = err.response.data.detail;
        } else if (Array.isArray(err.response.data.detail)) {
          // Validation errors array
          err.response.data.detail.forEach((e: any) => {
            if (e.loc && e.loc[1]) {
              errors[e.loc[1]] = e.msg;
            }
          });
          errorMessage = 'Validation error. Please check the highlighted fields.';
        } else if (err.response.data.detail.email) {
          errorMessage = err.response.data.detail.email;
        }
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setFieldErrors(errors);
      setError(`❌ ${errorMessage}`);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <p className="mt-4 text-gray-600">Loading doctors...</p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-8">
        <Link href="/appointments" className="text-blue-600 hover:text-blue-700 mb-4 inline-block">
          ← Back to Appointments
        </Link>
        <h1 className="text-3xl font-bold text-gray-900">Book an Appointment</h1>
        <p className="mt-2 text-gray-600">{isHospitalAdmin ? 'Schedule a consultation for a patient' : 'Schedule a consultation with one of our doctors'}</p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-500 text-red-800 rounded">
          <p className="font-semibold">Error</p>
          <p className="text-sm mt-1">{error}</p>
        </div>
      )}

      {success && (
        <div className="mb-6 p-4 bg-green-50 border-l-4 border-green-500 text-green-800 rounded">
          <p className="font-semibold">Success!</p>
          <p className="text-sm mt-1">{success}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-6 space-y-6">
        {/* Patient Selection (Hospital Admin only) */}
        {isHospitalAdmin && (
          <div>
            <label htmlFor="patient_id" className="block text-sm font-medium text-gray-700 mb-2">
              Select Patient <span className="text-red-500">*</span>
            </label>
            <select
              id="patient_id"
              name="patient_id"
              value={formData.patient_id}
              onChange={handleChange}
              required={isHospitalAdmin}
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none ${
                fieldErrors.patient_id ? 'border-red-500 bg-red-50' : 'border-gray-300'
              }`}
            >
              <option value="">-- Select a Patient --</option>
              {patients.length === 0 ? (
                <option disabled>No patients available</option>
              ) : (
                patients.map((patient) => (
                  <option key={patient.id} value={patient.id}>
                    {patient.user.name} ({patient.user.email})
                  </option>
                ))
              )}
            </select>
            {fieldErrors.patient_id && (
              <p className="text-red-600 text-sm mt-1">⚠️ {fieldErrors.patient_id}</p>
            )}
          </div>
        )}

        {/* Doctor Selection */}
        <div>
          <label htmlFor="doctor_id" className="block text-sm font-medium text-gray-700 mb-2">
            Select Doctor <span className="text-red-500">*</span>
          </label>
          <select
            id="doctor_id"
            name="doctor_id"
            value={formData.doctor_id}
            onChange={handleChange}
            required
            className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none ${
              fieldErrors.doctor_id ? 'border-red-500 bg-red-50' : 'border-gray-300'
            }`}
          >
            <option value="">-- Select a Doctor --</option>
            {doctors.map((doctor) => (
              <option key={doctor.id} value={doctor.id}>
                {doctor.name} - {doctor.specialization} ({doctor.experience_years} years)
              </option>
            ))}
          </select>
          {fieldErrors.doctor_id && (
            <p className="text-red-600 text-sm mt-1">⚠️ {fieldErrors.doctor_id}</p>
          )}
        </div>

        {/* Appointment Date */}
        <div>
          <label htmlFor="appointment_date" className="block text-sm font-medium text-gray-700 mb-2">
            Appointment Date <span className="text-red-500">*</span>
          </label>
          <input
            type="date"
            id="appointment_date"
            name="appointment_date"
            value={formData.appointment_date}
            onChange={handleChange}
            required
            min={new Date().toISOString().split('T')[0]}
            className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none ${
              fieldErrors.appointment_date ? 'border-red-500 bg-red-50' : 'border-gray-300'
            }`}
          />
          {fieldErrors.appointment_date && (
            <p className="text-red-600 text-sm mt-1">⚠️ {fieldErrors.appointment_date}</p>
          )}
        </div>

        {/* Appointment Time */}
        <div>
          <label htmlFor="appointment_time" className="block text-sm font-medium text-gray-700 mb-2">
            Appointment Time <span className="text-red-500">*</span>
          </label>
          <input
            type="time"
            id="appointment_time"
            name="appointment_time"
            value={formData.appointment_time}
            onChange={handleChange}
            required
            min="09:00"
            max="16:59"
            className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none ${
              fieldErrors.appointment_time ? 'border-red-500 bg-red-50' : 'border-gray-300'
            }`}
          />
          <p className="mt-1 text-xs text-blue-600 font-medium">⏰ Available times: 09:00 AM - 04:59 PM</p>
          {formData.appointment_time && (
            formData.appointment_time >= '17:00' ? (
              <p className="text-red-600 text-sm mt-2 p-2 bg-red-50 rounded border border-red-200">
                ❌ Invalid time selected! Appointments are only available between 09:00 AM - 04:59 PM
              </p>
            ) : (
              <p className="text-green-600 text-sm mt-2">✅ Valid time selected</p>
            )
          )}
          {fieldErrors.appointment_time && (
            <p className="text-red-600 text-sm mt-1">⚠️ {fieldErrors.appointment_time}</p>
          )}
        </div>

        {/* Chief Complaint (Hospital Admin only) */}
        {isHospitalAdmin && (
          <div>
            <label htmlFor="chief_complaint" className="block text-sm font-medium text-gray-700 mb-2">
              Chief Complaint <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="chief_complaint"
              name="chief_complaint"
              value={formData.chief_complaint}
              onChange={handleChange}
              required={isHospitalAdmin}
              placeholder="e.g., Chest pain and shortness of breath"
              maxLength={500}
              className={`w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none ${
                fieldErrors.chief_complaint ? 'border-red-500 bg-red-50' : 'border-gray-300'
              }`}
            />
            {fieldErrors.chief_complaint && (
              <p className="text-red-600 text-sm mt-1">⚠️ {fieldErrors.chief_complaint}</p>
            )}
          </div>
        )}

        {/* Symptoms (Hospital Admin only) */}
        {isHospitalAdmin && (
          <div>
            <label htmlFor="symptoms" className="block text-sm font-medium text-gray-700 mb-2">
              Symptoms (Optional)
            </label>
            <textarea
              id="symptoms"
              name="symptoms"
              value={formData.symptoms}
              onChange={handleChange}
              placeholder="Describe patient symptoms"
              rows={3}
              maxLength={500}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none resize-none"
            />
          </div>
        )}

        {/* Notes */}
        <div>
          <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-2">
            Notes (Optional)
          </label>
          <textarea
            id="notes"
            name="notes"
            value={formData.notes}
            onChange={handleChange}
            placeholder={isHospitalAdmin ? "Additional appointment notes" : "Describe your symptoms or reason for visit"}
            rows={4}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none resize-none"
          />
        </div>

        {/* Submit Button */}
        <div className="flex gap-4">
          <button
            type="submit"
            disabled={submitting}
            className="flex-1 px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {submitting ? 'Booking...' : 'Book Appointment'}
          </button>
          <Link href="/appointments" className="flex-1">
            <button
              type="button"
              className="w-full px-6 py-3 bg-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-400 transition-colors"
            >
              Cancel
            </button>
          </Link>
        </div>
      </form>
    </div>
  );
}
