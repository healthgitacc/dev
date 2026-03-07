'use client';

import { useState } from 'react';
import apiClient from '@/lib/api';
import { useAuthStore } from '@/lib/auth-store';
import { useRouter } from 'next/navigation';
import LoadingSpinner from '@/components/common/LoadingSpinner';

interface DoctorFormData {
  name: string;
  email: string;
  phone: string;
  specialization: string;
  experience_years: string;
  license_number: string;
}

export default function AddDoctorPage() {
  const { user } = useAuthStore();
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  
  const [formData, setFormData] = useState<DoctorFormData>({
    name: '',
    email: '',
    phone: '',
    specialization: '',
    experience_years: '',
    license_number: '',
  });

  const specializations = [
    'Cardiology',
    'Neurology',
    'Orthopedics',
    'Pediatrics',
    'Dermatology',
    'Psychiatry',
    'Ophthalmology',
    'ENT (Ear, Nose & Throat)',
    'General Medicine',
    'Surgery',
    'Gynecology',
    'Dentistry',
    'Radiology',
    'Pathology',
    'Anesthesiology'
  ];

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const validateForm = (): string | null => {
    if (!formData.name.trim()) return 'Doctor name is required';
    if (!formData.email.trim()) return 'Email is required';
    if (!/\S+@\S+\.\S+/.test(formData.email)) return 'Invalid email format';
    if (!formData.phone.trim()) return 'Phone number is required';
    if (!/^\+?[0-9]{10,15}$/.test(formData.phone)) return 'Invalid phone number format';
    if (!formData.specialization) return 'Specialization is required';
    if (!formData.experience_years) return 'Experience years is required';
    if (parseInt(formData.experience_years) < 0) return 'Experience years cannot be negative';
    if (!formData.license_number.trim()) return 'License number is required';
    
    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const response = await apiClient.post('/api/admin/doctors', {
        name: formData.name.trim(),
        email: formData.email.trim(),
        phone: formData.phone.trim(),
        specialization: formData.specialization,
        experience_years: parseInt(formData.experience_years),
        license_number: formData.license_number.trim(),
      });

      setSuccess(true);
      setFormData({
        name: '',
        email: '',
        phone: '',
        specialization: '',
        experience_years: '',
        license_number: '',
      });
      
      // Redirect to doctors page after 2 seconds
      setTimeout(() => {
        router.push('/doctors');
      }, 2000);

    } catch (err: any) {
      console.error('Error adding doctor:', err);
      setError(err.response?.data?.detail || 'Failed to add doctor. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!user || (user.role !== 'hospital_admin' && user.role !== 'super_admin')) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Access Denied</h2>
        <p className="text-gray-600">You don't have permission to access this page.</p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Add New Doctor</h1>
        <button
          onClick={() => router.push('/doctors')}
          className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
        >
          Back to Doctors
        </button>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-100 text-red-700 rounded-lg">
          {error}
        </div>
      )}

      {success && (
        <div className="mb-6 p-4 bg-green-100 text-green-700 rounded-lg">
          Doctor added successfully! SMS notification sent to the doctor. Redirecting to doctors page...
        </div>
      )}

      <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Doctor Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Doctor Name *
              </label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                placeholder="Dr. John Smith"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent"
                disabled={loading}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Specialization *
              </label>
              <select
                name="specialization"
                value={formData.specialization}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent"
                disabled={loading}
              >
                <option value="">Select specialization</option>
                {specializations.map((spec) => (
                  <option key={spec} value={spec}>
                    {spec}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Experience Years *
              </label>
              <input
                type="number"
                name="experience_years"
                value={formData.experience_years}
                onChange={handleChange}
                placeholder="5"
                min="0"
                max="50"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent"
                disabled={loading}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                License Number *
              </label>
              <input
                type="text"
                name="license_number"
                value={formData.license_number}
                onChange={handleChange}
                placeholder="MED123456"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent"
                disabled={loading}
              />
            </div>
          </div>

          {/* Contact Information */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Contact Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email Address *
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="doctor@example.com"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent"
                  disabled={loading}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Phone Number *
                </label>
                <input
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                  placeholder="+1234567890"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent"
                  disabled={loading}
                />
              </div>
            </div>
          </div>

          {/* Form Actions */}
          <div className="flex gap-4">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 min-w-[200px] px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="flex items-center justify-center">
                  <LoadingSpinner size="sm" text="Adding Doctor..." className="text-white" />
                </div>
              ) : (
                'Add Doctor & Send SMS'
              )}
            </button>
            
            <button
              type="button"
              onClick={() => router.push('/doctors')}
              disabled={loading}
              className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium disabled:opacity-50"
            >
              Cancel
            </button>
          </div>

          {/* Information */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <div className="text-blue-600 text-lg">ℹ️</div>
              <div>
                <h4 className="font-medium text-blue-900">What happens next?</h4>
                <p className="text-sm text-blue-800 mt-1">
                  • A temporary password will be generated for the doctor
                  <br />
                  • An SMS notification will be sent to the doctor's phone number
                  <br />
                  • The doctor can log in and change their password
                </p>
              </div>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}