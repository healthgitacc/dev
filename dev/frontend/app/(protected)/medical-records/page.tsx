'use client';

import { useState, useEffect } from 'react';
import apiClient from '@/lib/api';

interface MedicalRecord {
  id: number;
  patient_id: number;
  doctor_id: number;
  diagnosis: string;
  treatment: string;
  notes: string;
  created_at: string;
  updated_at: string;
  doctor: {
    id: number;
    name: string;
    specialization: string;
  };
}

export default function MedicalRecordsPage() {
  const [records, setRecords] = useState<MedicalRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchRecords = async () => {
      try {
        setLoading(true);
        const response = await apiClient.get('/api/medical-records');
        setRecords(response.data.items || []);
        setError('');
      } catch (err) {
        setError('Failed to load medical records');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchRecords();
  }, []);

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

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <p className="mt-4 text-gray-600">Loading medical records...</p>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Medical Records</h1>

      {error && (
        <div className="mb-6 p-4 bg-red-100 text-red-700 rounded-lg">
          {error}
        </div>
      )}

      {records.length > 0 ? (
        <div className="space-y-4">
          {records.map((record) => (
            <div
              key={record.id}
              className="bg-white rounded-lg shadow-sm p-6 border border-gray-200 hover:shadow-md transition-shadow"
            >
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">
                    {record.doctor?.name || 'Dr. Unknown'}
                  </h3>
                  <p className="text-sm text-blue-600">
                    {record.doctor?.specialization || 'N/A'}
                  </p>
                </div>
                <span className="text-xs text-gray-500">
                  {formatDate(record.created_at)}
                </span>
              </div>

              <div className="space-y-3">
                {record.diagnosis && (
                  <div>
                    <p className="text-xs font-medium text-gray-600 uppercase">
                      Diagnosis
                    </p>
                    <p className="text-sm text-gray-700">{record.diagnosis}</p>
                  </div>
                )}

                {record.treatment && (
                  <div>
                    <p className="text-xs font-medium text-gray-600 uppercase">
                      Treatment
                    </p>
                    <p className="text-sm text-gray-700">{record.treatment}</p>
                  </div>
                )}

                {record.notes && (
                  <div>
                    <p className="text-xs font-medium text-gray-600 uppercase">
                      Notes
                    </p>
                    <p className="text-sm text-gray-700">{record.notes}</p>
                  </div>
                )}
              </div>

              <div className="mt-4 pt-4 border-t border-gray-200">
                <button className="text-sm text-blue-600 hover:text-blue-700 font-medium">
                  View Full Details
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm p-12 text-center border border-gray-200">
          <div className="text-4xl mb-4">📋</div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            No medical records yet
          </h2>
          <p className="text-gray-600">
            Your medical records from doctors will appear here.
          </p>
        </div>
      )}
    </div>
  );
}
