'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import apiClient from '@/lib/api';

export default function AddPatientPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    blood_group: '',
    gender: '',
    date_of_birth: '',
    address: '',
    medical_history: '',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      // Validate required fields
      if (!formData.name.trim()) {
        throw new Error('Patient name is required');
      }
      if (!formData.email.trim()) {
        throw new Error('Patient email is required');
      }
      if (!formData.phone.trim()) {
        throw new Error('Patient phone is required');
      }

      // Build request payload with optional fields only if they have values
      const payload: any = {
        name: formData.name,
        email: formData.email,
        phone: formData.phone,
      };

      if (formData.blood_group) payload.blood_group = formData.blood_group;
      if (formData.gender) payload.gender = formData.gender;
      if (formData.date_of_birth) payload.date_of_birth = formData.date_of_birth;
      if (formData.address) payload.address = formData.address;
      if (formData.medical_history) payload.medical_history = formData.medical_history;

      const response = await apiClient.post('/api/admin/patients', payload);

      setSuccess('Patient added successfully! SMS notification has been sent.');
      
      // Reset form
      setFormData({
        name: '',
        email: '',
        phone: '',
        blood_group: '',
        gender: '',
        date_of_birth: '',
        address: '',
        medical_history: '',
      });

      // Redirect to patients page after 2 seconds
      setTimeout(() => {
        router.push('/patients');
      }, 2000);
    } catch (err: any) {
      let errorMessage = 'Failed to add patient';
      
      // Try to extract error message from response
      if (err.response?.data?.detail) {
        const detail = err.response.data.detail;
        if (typeof detail === 'object' && detail.message) {
          errorMessage = detail.message;
        } else if (typeof detail === 'string') {
          errorMessage = detail;
        } else {
          errorMessage = JSON.stringify(detail);
        }
      } else if (err.response?.data?.message) {
        errorMessage = err.response.data.message;
      } else if (err.response?.data?.error) {
        const error = err.response.data.error;
        if (typeof error === 'object' && error.message) {
          errorMessage = error.message;
        } else if (typeof error === 'string') {
          errorMessage = error;
        }
      } else if (typeof err.response?.data === 'string') {
        errorMessage = err.response.data;
      } else if (err.response?.data && typeof err.response.data === 'object') {
        if (err.response.data.message) {
          errorMessage = err.response.data.message;
        } else {
          errorMessage = JSON.stringify(err.response.data);
        }
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      // Add status context to specific errors
      if (err.response?.status === 409) {
        // Extract email from message if it contains one
        const emailMatch = errorMessage.match(/[\w\.-]+@[\w\.-]+\.\w+/);
        const email = emailMatch ? emailMatch[0] : errorMessage;
        errorMessage = `Email already registered: ${email}`;
      } else if (err.response?.status === 400) {
        errorMessage = `Invalid input: ${errorMessage}`;
      } else if (err.response?.status === 403) {
        errorMessage = `Permission denied: ${errorMessage}`;
      } else if (err.response?.status === 500) {
        errorMessage = `Server error: ${errorMessage}`;
      }
      
      setError(errorMessage);
      console.error('Error adding patient:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <div className="mb-6">
        <Link href="/patients" className="text-blue-600 hover:text-blue-800 text-sm font-medium">
          ← Back to Patients
        </Link>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Add New Patient</h1>

        {error && (
          <div className="mb-6 p-4 bg-red-50 text-red-800 rounded-lg border-2 border-red-400 shadow-sm">
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 mt-0.5">
                <svg className="w-5 h-5 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="flex-1">
                <h3 className="font-bold text-red-800 mb-1">Error Adding Patient</h3>
                <p className="text-red-700 text-sm">{error}</p>
              </div>
            </div>
          </div>
        )}

        {success && (
          <div className="mb-6 p-4 bg-green-50 text-green-800 rounded-lg border-2 border-green-400 shadow-sm">
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 mt-0.5">
                <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="flex-1">
                <h3 className="font-bold text-green-800 mb-1">Patient Added Successfully!</h3>
                <p className="text-green-700 text-sm">{success}</p>
                <p className="text-green-600 text-xs mt-2">Redirecting to patients list...</p>
              </div>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Required Fields Section */}
          <div className="border-b border-gray-200 pb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Required Information</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Name */}
              <div className="md:col-span-2">
                <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                  Full Name *
                </label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  placeholder="e.g., John Doe"
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent"
                />
              </div>

              {/* Email */}
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                  Email *
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="e.g., john@example.com"
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent"
                />
              </div>

              {/* Phone */}
              <div>
                <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">
                  Phone Number *
                </label>
                <input
                  type="tel"
                  id="phone"
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                  placeholder="e.g., +1234567890"
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent"
                />
              </div>
            </div>
          </div>

          {/* Optional Fields Section */}
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Optional Information</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Gender */}
              <div>
                <label htmlFor="gender" className="block text-sm font-medium text-gray-700 mb-2">
                  Gender
                </label>
                <select
                  id="gender"
                  name="gender"
                  value={formData.gender}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent"
                >
                  <option value="">Select Gender</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                </select>
              </div>

              {/* Blood Group */}
              <div>
                <label htmlFor="blood_group" className="block text-sm font-medium text-gray-700 mb-2">
                  Blood Group
                </label>
                <select
                  id="blood_group"
                  name="blood_group"
                  value={formData.blood_group}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent"
                >
                  <option value="">Select Blood Group</option>
                  <option value="O+">O+</option>
                  <option value="O-">O-</option>
                  <option value="A+">A+</option>
                  <option value="A-">A-</option>
                  <option value="B+">B+</option>
                  <option value="B-">B-</option>
                  <option value="AB+">AB+</option>
                  <option value="AB-">AB-</option>
                </select>
              </div>

              {/* Date of Birth */}
              <div>
                <label htmlFor="date_of_birth" className="block text-sm font-medium text-gray-700 mb-2">
                  Date of Birth
                </label>
                <input
                  type="date"
                  id="date_of_birth"
                  name="date_of_birth"
                  value={formData.date_of_birth}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent"
                />
              </div>

              {/* Address */}
              <div className="md:col-span-2">
                <label htmlFor="address" className="block text-sm font-medium text-gray-700 mb-2">
                  Address
                </label>
                <input
                  type="text"
                  id="address"
                  name="address"
                  value={formData.address}
                  onChange={handleChange}
                  placeholder="e.g., 123 Main St, City, State"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent"
                />
              </div>

              {/* Medical History */}
              <div className="md:col-span-2">
                <label htmlFor="medical_history" className="block text-sm font-medium text-gray-700 mb-2">
                  Medical History
                </label>
                <textarea
                  id="medical_history"
                  name="medical_history"
                  value={formData.medical_history}
                  onChange={handleChange}
                  placeholder="e.g., Allergic to Penicillin, previous surgeries, chronic conditions..."
                  rows={4}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent resize-none"
                />
              </div>
            </div>
          </div>

          {/* Buttons */}
          <div className="flex gap-4 pt-6 border-t border-gray-200">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium"
            >
              {loading ? 'Adding Patient...' : 'Add Patient'}
            </button>
            <Link href="/patients" className="flex-1">
              <button
                type="button"
                className="w-full px-6 py-2 bg-gray-300 text-gray-900 rounded-lg hover:bg-gray-400 transition-colors font-medium"
              >
                Cancel
              </button>
            </Link>
          </div>
        </form>

        <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-sm text-gray-700">
            <span className="font-semibold">Note:</span> Patient will receive an SMS notification with temporary credentials after being added.
          </p>
        </div>
      </div>
    </div>
  );
}
