'use client';

import { useState, useEffect } from 'react';
import apiClient from '@/lib/api';
import Link from 'next/link';

interface Patient {
  id: number;
  user_id: number;
  name: string;
  email: string;
  phone: string;
  age?: number;
  gender?: string;
  blood_group?: string;
  medical_history?: string;
  is_active: boolean;
  created_at: string;
}

export default function PatientsPage() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filteredPatients, setFilteredPatients] = useState<Patient[]>([]);

  // Fetch patients
  useEffect(() => {
    const fetchPatients = async () => {
      try {
        setLoading(true);
        const response = await apiClient.get('/api/patients');
        const patientsList = response.data.items || [];
        setPatients(patientsList);
        setFilteredPatients(patientsList);
        setError('');
      } catch (err) {
        setError('Failed to load patients');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchPatients();
  }, []);

  // Filter patients based on search
  useEffect(() => {
    const filtered = patients.filter((patient) =>
      patient.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      patient.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      patient.phone.includes(searchTerm)
    );
    setFilteredPatients(filtered);
  }, [searchTerm, patients]);

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <p className="mt-4 text-gray-600">Loading patients...</p>
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Patients</h1>
        <Link href="/add-patient">
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium">
            Add Patient
          </button>
        </Link>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-100 text-red-700 rounded-lg">
          {error}
        </div>
      )}

      {/* Search and Filter */}
      <div className="mb-6 bg-white rounded-lg shadow-sm p-4 border border-gray-200">
        <input
          type="text"
          placeholder="Search by name, email, or phone..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent"
        />
      </div>

      {/* Patients Table or Cards */}
      {filteredPatients.length > 0 ? (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Patient Name</th>
                  <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Email</th>
                  <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Phone</th>
                  <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Blood Group</th>
                  <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Status</th>
                  <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {filteredPatients.map((patient) => (
                  <tr key={patient.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm text-gray-900 font-medium">{patient.name}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{patient.email}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{patient.phone}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {patient.blood_group || 'N/A'}
                    </td>
                    <td className="px-6 py-4 text-sm">
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-medium ${
                          patient.is_active
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {patient.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm space-x-2">
                      <Link href={`/patients/${patient.id}`}>
                        <button className="text-blue-600 hover:text-blue-700 font-medium">
                          View
                        </button>
                      </Link>
                      <button className="text-gray-600 hover:text-gray-700 ml-4">
                        Edit
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm p-12 text-center border border-gray-200">
          <div className="text-4xl mb-4">👥</div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            {patients.length === 0 ? 'No patients found' : 'No matching patients'}
          </h2>
          <p className="text-gray-600 mb-6">
            {patients.length === 0
              ? 'Start by adding the first patient to the system.'
              : 'Try adjusting your search criteria.'}
          </p>
          {patients.length === 0 && (
            <Link href="/add-patient">
              <button className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                Add First Patient
              </button>
            </Link>
          )}
        </div>
      )}
    </div>
  );
}
