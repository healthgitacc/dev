'use client';

import { useState, useEffect } from 'react';
import apiClient from '@/lib/api';
import Link from 'next/link';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import { useAuthStore } from '@/lib/auth-store';
import { useRouter } from 'next/navigation';

interface Doctor {
  id: number;
  name: string;
  email: string;
  phone: string;
  specialization: string;
  experience_years: number;
  license_number: string | null;
}

export default function DoctorsPage() {
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [filteredDoctors, setFilteredDoctors] = useState<Doctor[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSpecialization, setSelectedSpecialization] = useState('All');
  const [specializations, setSpecializations] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Fetch all doctors
  useEffect(() => {
    const fetchDoctors = async () => {
      try {
        setLoading(true);
        const response = await apiClient.get('/api/doctors?limit=100');
        const doctorsList = response.data.items || [];
        setDoctors(doctorsList);
        
        // Extract unique specializations
        const specs = Array.from(new Set(
          doctorsList.map((doc: Doctor) => doc.specialization).filter(Boolean)
        )) as string[];
        setSpecializations(specs.sort());
        
        setFilteredDoctors(doctorsList);
        setError('');
      } catch (err) {
        // If fetching fails, try to get specializations separately
        try {
          const specsResponse = await apiClient.get('/api/doctors/list/specializations');
          const specs = specsResponse.data.specializations || [];
          setSpecializations(specs.sort());
        } catch (specErr) {
          console.error('Error fetching specializations:', specErr);
        }
        setError('Failed to load doctors');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchDoctors();
  }, []);

  // Filter doctors based on search and specialization
  useEffect(() => {
    let filtered = doctors;

    // Filter by specialization
    if (selectedSpecialization !== 'All') {
      filtered = filtered.filter(
        (doc) => doc.specialization === selectedSpecialization
      );
    }

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(
        (doc) =>
          doc.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          doc.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
          doc.specialization.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    setFilteredDoctors(filtered);
  }, [searchTerm, selectedSpecialization, doctors]);

  if (loading) {
    return (
      <div className="text-center py-12">
        <LoadingSpinner size="lg" text="Loading doctors..." />
      </div>
    );
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Doctors</h1>
        <Link href="/admin/add-doctor">
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm">
            Add New Doctor
          </button>
        </Link>
      </div>
      
      {error && (
        <div className="mb-6 p-4 bg-red-100 text-red-700 rounded-lg">
          {error}
        </div>
      )}

      {/* Search and Filter */}
      <div className="mb-6 bg-white rounded-lg shadow-sm p-6 border border-gray-200">
        <div className="flex gap-4 flex-col md:flex-row">
          <input
            type="text"
            placeholder="Search by doctor name, specialization, or email..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent"
          />
          <select 
            value={selectedSpecialization}
            onChange={(e) => setSelectedSpecialization(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent md:w-56"
          >
            <option value="All">All Specializations</option>
            {specializations.map((spec) => (
              <option key={spec} value={spec}>
                {spec}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Results Count */}
      <div className="mb-4 text-sm text-gray-600">
        Found {filteredDoctors.length} doctor{filteredDoctors.length !== 1 ? 's' : ''}
      </div>

      {/* Doctors Grid */}
      {filteredDoctors.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredDoctors.map((doctor) => (
            <div key={doctor.id} className="bg-white rounded-lg shadow-sm p-6 border border-gray-200 hover:shadow-md transition-shadow">
              <div className="text-4xl mb-4">👨‍⚕️</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-1">{doctor.name}</h3>
              <p className="text-sm font-medium text-blue-600 mb-2">{doctor.specialization}</p>
              <div className="text-xs text-gray-600 space-y-1 mb-4">
                <p>📧 {doctor.email}</p>
                <p>📱 {doctor.phone}</p>
                <p>⏱️ {doctor.experience_years || 0} years experience</p>
                {doctor.license_number && (
                  <p>📜 License: {doctor.license_number}</p>
                )}
              </div>
              <Link href={`/book-appointment?doctor_id=${doctor.id}`}>
                <button className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium">
                  Book Appointment Now
                </button>
              </Link>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm p-12 border border-gray-200 text-center">
          <div className="text-4xl mb-4">🔍</div>
          <p className="text-gray-600">No doctors found matching your criteria.</p>
          <button
            onClick={() => {
              setSearchTerm('');
              setSelectedSpecialization('All');
            }}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Clear Filters
          </button>
        </div>
      )}
    </div>
  );
}
