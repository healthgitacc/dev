'use client';

import React, { useState, useEffect } from 'react';
import { Hospital } from '@/lib/types';
import apiClient from '@/lib/api';

const SuperOwnerPage: React.FC = () => {
  const [hospitals, setHospitals] = useState<Hospital[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

  // Form state for adding hospital
  const [newHospital, setNewHospital] = useState({
    name: '',
    email: '',
    phone: '',
    address: ''
  });

  useEffect(() => {
    fetchHospitals();
  }, []);

  const fetchHospitals = async () => {
    try {
      setLoading(true);
      setMessage(null);
      
      const response = await apiClient.get('/api/admin/hospitals');
      
      if (response.data && response.data.items) {
        setHospitals(response.data.items);
      } else if (Array.isArray(response.data)) {
        setHospitals(response.data);
      } else {
        console.error('Unexpected response format:', response.data);
        setMessage({ type: 'error', text: 'Unexpected response format from server' });
      }
    } catch (error: any) {
      console.error('Error fetching hospitals:', error);
      const errorMsg = error.response?.data?.detail || error.message || 'Failed to fetch hospitals';
      setMessage({ type: 'error', text: errorMsg });
    } finally {
      setLoading(false);
    }
  };

  const handleAddHospital = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage(null);
    
    try {
      // Backend expects query parameters for create_hospital based on the code I saw earlier
      // Wait, let me re-check create_hospital in hospital_routes.py
      /*
      @router.post("")
      async def create_hospital(
          name: str = Query(..., ...),
          email: str = Query(..., ...),
          ...
      )
      */
      // If it uses Query, then it expects them in the URL query string, not body.
      
      const params = new URLSearchParams();
      params.append('name', newHospital.name);
      params.append('email', newHospital.email);
      if (newHospital.phone) params.append('phone', newHospital.phone);
      if (newHospital.address) params.append('address', newHospital.address);

      const response = await apiClient.post(`/api/admin/hospitals?${params.toString()}`);

      if (response.status === 201 || response.status === 200) {
        setMessage({ type: 'success', text: 'Hospital created successfully' });
        setShowAddModal(false);
        setNewHospital({ name: '', email: '', phone: '', address: '' });
        fetchHospitals();
      } else {
        setMessage({ type: 'error', text: 'Failed to create hospital' });
      }
    } catch (error: any) {
      console.error('Error creating hospital:', error);
      const errorMsg = error.response?.data?.detail || error.message || 'Failed to create hospital';
      setMessage({ type: 'error', text: errorMsg });
    }
  };

  const handleHospitalAction = async (hospitalId: number, action: string) => {
    setMessage(null);
    try {
      let endpoint = '';
      let method: 'put' | 'delete' = 'put';
      
      switch (action) {
        case 'activate':
          endpoint = `/api/admin/hospitals/${hospitalId}/activate`;
          method = 'put';
          break;
        case 'deactivate':
          endpoint = `/api/admin/hospitals/${hospitalId}/deactivate`;
          method = 'put';
          break;
        case 'delete':
          endpoint = `/api/admin/hospitals/${hospitalId}`;
          method = 'delete';
          break;
        default:
          return;
      }

      const response = await (method === 'put' ? apiClient.put(endpoint) : apiClient.delete(endpoint));

      if (response.status === 200) {
        const actionText = action === 'activate' ? 'activated' : 
                          action === 'deactivate' ? 'deactivated' : 'deleted';
        setMessage({ type: 'success', text: `Hospital ${actionText} successfully` });
        fetchHospitals();
      } else {
        setMessage({ type: 'error', text: `Failed to ${action} hospital` });
      }
    } catch (error: any) {
      console.error(`Error ${action}ing hospital:`, error);
      const errorMsg = error.response?.data?.detail || error.message || `Failed to ${action} hospital`;
      setMessage({ type: 'error', text: errorMsg });
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-300 rounded w-1/4 mb-6"></div>
            <div className="bg-white rounded-lg shadow">
              <div className="h-12 bg-gray-200 rounded-t-lg"></div>
              <div className="p-6">
                <div className="space-y-4">
                  {[...Array(5)].map((_, i) => (
                    <div key={i} className="h-16 bg-gray-200 rounded"></div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Hospital Management</h1>
          <p className="mt-2 text-gray-600">
            Manage hospitals across the healthcare network
          </p>
        </div>

        {/* Message */}
        {message && (
          <div className={`mb-6 rounded-lg p-4 ${
            message.type === 'success' 
              ? 'bg-green-50 border border-green-200 text-green-700' 
              : 'bg-red-50 border border-red-200 text-red-700'
          }`}>
            <p className="text-sm">{message.text}</p>
          </div>
        )}

        {/* Controls */}
        <div className="mb-6 flex justify-between items-center">
          <div className="text-sm text-gray-600">
            Total Hospitals: {hospitals.length}
          </div>
          <button 
            onClick={() => setShowAddModal(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
          >
            + Add Hospital
          </button>
        </div>

        {/* Hospitals Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-1/3">
                  Hospital Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-1/3">
                  Email
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-1/6">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-1/6">
                  Created Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-1/6">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {hospitals.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-gray-500">
                    No hospitals found. Add your first hospital to get started.
                  </td>
                </tr>
              ) : (
                hospitals.map((hospital) => (
                  <tr key={hospital.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {hospital.name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {hospital.email}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        hospital.status === 'active' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {hospital.status.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(hospital.created_at)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                      {hospital.status === 'active' ? (
                        <button
                          onClick={() => handleHospitalAction(hospital.id, 'deactivate')}
                          className="text-red-600 hover:text-red-900 border border-red-600 hover:bg-red-50 px-3 py-1 rounded text-sm"
                        >
                          Deactivate
                        </button>
                      ) : (
                        <button
                          onClick={() => handleHospitalAction(hospital.id, 'activate')}
                          className="text-green-600 hover:text-green-900 border border-green-600 hover:bg-green-50 px-3 py-1 rounded text-sm"
                        >
                          Activate
                        </button>
                      )}
                      <button
                        onClick={() => handleHospitalAction(hospital.id, 'delete')}
                        className="text-red-600 hover:text-red-900 border border-red-600 hover:bg-red-50 px-3 py-1 rounded text-sm"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add Hospital Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Add New Hospital</h2>
            </div>
            <form onSubmit={handleAddHospital} className="px-6 py-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Hospital Name *
                </label>
                <input
                  type="text"
                  value={newHospital.name}
                  onChange={(e) => setNewHospital({...newHospital, name: e.target.value})}
                  placeholder="Enter hospital name"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email *
                </label>
                <input
                  type="email"
                  value={newHospital.email}
                  onChange={(e) => setNewHospital({...newHospital, email: e.target.value})}
                  placeholder="Enter hospital email"
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Phone
                </label>
                <input
                  type="tel"
                  value={newHospital.phone}
                  onChange={(e) => setNewHospital({...newHospital, phone: e.target.value})}
                  placeholder="Enter hospital phone"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Address
                </label>
                <input
                  type="text"
                  value={newHospital.address}
                  onChange={(e) => setNewHospital({...newHospital, address: e.target.value})}
                  placeholder="Enter hospital address"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Create Hospital
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default SuperOwnerPage;
