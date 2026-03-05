'use client';

import { useState, useEffect } from 'react';
import apiClient from '@/lib/api';

interface MedicalRecord {
  id: number;
  patient_id: number;
  patient_name?: string;
  doctor_id: number;
  doctor_name?: string;
  disease_name?: string;
  diagnosis: string;
  prescription_text?: string;
  dosage?: string;
  follow_up_date?: string;
  notes: string;
  treatment?: string;
  created_at: string;
  updated_at: string;
  doctor?: {
    id: number;
    name: string;
    specialization: string;
  };
}

// Dummy medical reports for demonstration
const DUMMY_REPORTS: MedicalRecord[] = [
  {
    id: 101,
    patient_id: 1,
    patient_name: 'John Doe',
    doctor_id: 1,
    doctor_name: 'Dr. Sarah Anderson',
    disease_name: 'Hypertension',
    diagnosis: 'Patient presents with elevated blood pressure readings (150/95 mmHg). BP monitor at home shows consistent readings above normal range. No symptoms reported.',
    prescription_text: 'Lisinopril 10mg',
    dosage: 'Once daily in the morning',
    follow_up_date: '2026-04-05T10:00:00',
    notes: 'Advised dietary modifications and light exercise. Monitor BP daily.',
    created_at: '2026-03-01T10:30:00',
    updated_at: '2026-03-01T10:30:00',
    doctor: {
      id: 1,
      name: 'Dr. Sarah Anderson',
      specialization: 'Cardiology',
    },
  },
  {
    id: 102,
    patient_id: 2,
    patient_name: 'Jane Smith',
    doctor_id: 2,
    doctor_name: 'Dr. Michael Chen',
    disease_name: 'Type 2 Diabetes',
    diagnosis: 'Lab results show fasting glucose 185 mg/dL and HbA1c 8.2%. Patient reports increased thirst and frequent urination.',
    prescription_text: 'Metformin 500mg',
    dosage: 'Twice daily with meals',
    follow_up_date: '2026-04-12T14:00:00',
    notes: 'Referred to nutritionist. Start exercise program. Recheck labs in 3 months.',
    created_at: '2026-02-28T14:15:00',
    updated_at: '2026-02-28T14:15:00',
    doctor: {
      id: 2,
      name: 'Dr. Michael Chen',
      specialization: 'Endocrinology',
    },
  },
  {
    id: 103,
    patient_id: 3,
    patient_name: 'Robert Wilson',
    doctor_id: 3,
    doctor_name: 'Dr. Emily Rodriguez',
    disease_name: 'Acute Upper Respiratory Infection',
    diagnosis: 'Patient presents with cough, sore throat, and mild fever (37.8°C). Physical exam shows inflamed throat. Rapid strep test negative.',
    prescription_text: 'Azithromycin 500mg',
    dosage: 'Once daily for 3 days',
    follow_up_date: '2026-03-08T11:00:00',
    notes: 'Rest, fluids, and honey for throat. Return if symptoms worsen.',
    created_at: '2026-03-02T09:45:00',
    updated_at: '2026-03-02T09:45:00',
    doctor: {
      id: 3,
      name: 'Dr. Emily Rodriguez',
      specialization: 'General Practice',
    },
  },
  {
    id: 104,
    patient_id: 4,
    patient_name: 'Maria Garcia',
    doctor_id: 4,
    doctor_name: 'Dr. James Thompson',
    disease_name: 'Migraine with Aura',
    diagnosis: 'Patient reports frequent migraines occurring 2-3 times per week with visual auras 20 minutes before onset. Stress and lack of sleep identified as triggers.',
    prescription_text: 'Sumatriptan 50mg',
    dosage: 'As needed for migraine onset',
    follow_up_date: '2026-03-22T13:00:00',
    notes: 'Avoid known triggers. Started preventive therapy. Migraine diary recommended.',
    created_at: '2026-02-26T16:20:00',
    updated_at: '2026-02-26T16:20:00',
    doctor: {
      id: 4,
      name: 'Dr. James Thompson',
      specialization: 'Neurology',
    },
  },
  {
    id: 105,
    patient_id: 5,
    patient_name: 'Lisa Anderson',
    doctor_id: 1,
    doctor_name: 'Dr. Sarah Anderson',
    disease_name: 'Atrial Fibrillation',
    diagnosis: 'ECG shows irregular atrial fibrillation with ventricular rate 95-110 bpm. Echocardiogram shows normal cardiac structure. No chest pain or shortness of breath.',
    prescription_text: 'Warfarin 5mg, Metoprolol 25mg',
    dosage: 'Warfarin once daily, Metoprolol twice daily',
    follow_up_date: '2026-03-15T09:30:00',
    notes: 'INR monitoring required. Anticoagulation therapy started. Avoid NSAIDs.',
    created_at: '2026-02-25T11:00:00',
    updated_at: '2026-02-25T11:00:00',
    doctor: {
      id: 1,
      name: 'Dr. Sarah Anderson',
      specialization: 'Cardiology',
    },
  },
];

export default function MedicalRecordsPage() {
  const [records, setRecords] = useState<MedicalRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showDummy, setShowDummy] = useState(false);

  useEffect(() => {
    const fetchRecords = async () => {
      try {
        setLoading(true);
        const response = await apiClient.get('/api/medical-records');
        const recordsList = response.data.items || [];
        
        if (recordsList.length === 0) {
          // Show dummy data if no real records exist
          setRecords(DUMMY_REPORTS);
          setShowDummy(true);
        } else {
          setRecords(recordsList);
          setShowDummy(false);
        }
        setError('');
      } catch (err) {
        // If error, show dummy data for demo
        setRecords(DUMMY_REPORTS);
        setShowDummy(true);
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

  const downloadReport = (record: MedicalRecord) => {
    // Create report content
    const reportContent = `
================================================================================
                        MEDICAL REPORT
================================================================================

Report ID: ${record.id}
Date: ${formatDate(record.created_at)}
Last Updated: ${formatDate(record.updated_at)}

================================================================================
PATIENT INFORMATION
================================================================================
Name: ${record.patient_name || 'N/A'}
Patient ID: ${record.patient_id}

================================================================================
DOCTOR INFORMATION
================================================================================
Doctor Name: ${record.doctor_name || 'N/A'}
Specialization: ${record.doctor?.specialization || 'N/A'}
Doctor ID: ${record.doctor_id}

================================================================================
DIAGNOSIS
================================================================================
Disease/Condition: ${record.disease_name || 'N/A'}
Diagnosis: ${record.diagnosis || 'N/A'}

================================================================================
TREATMENT PLAN
================================================================================
Prescription: ${record.prescription_text || 'N/A'}
Dosage: ${record.dosage || 'N/A'}
Treatment: ${record.treatment || 'N/A'}

================================================================================
CLINICAL NOTES
================================================================================
${record.notes || 'No additional notes'}

================================================================================
FOLLOW-UP
================================================================================
Follow-up Date: ${record.follow_up_date ? formatDate(record.follow_up_date) : 'N/A'}

================================================================================
                    END OF MEDICAL REPORT
================================================================================

This is an official medical record. Please keep it safe and share with other healthcare providers as needed.
Generated on: ${new Date().toLocaleString()}
    `.trim();

    // Create blob and download
    const blob = new Blob([reportContent], { type: 'text/plain;charset=utf-8' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    // Generate filename
    const patientName = record.patient_name?.replace(/\s+/g, '_') || 'Patient';
    const doctorName = record.doctor_name?.replace(/\s+/g, '_') || 'Report';
    const timestamp = new Date().toISOString().split('T')[0];
    const filename = `Medical_Report_${patientName}_${doctorName}_${timestamp}.txt`;
    
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
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
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">📋 Medical Records</h1>
        {showDummy && (
          <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">
            Demo / Sample Data
          </span>
        )}
      </div>

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
              {/* Header */}
              <div className="flex justify-between items-start mb-4 pb-4 border-b border-gray-200">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-2xl">👨‍⚕️</span>
                    <h3 className="text-lg font-semibold text-gray-900">
                      {record.doctor?.name || record.doctor_name || 'Dr. Unknown'}
                    </h3>
                  </div>
                  <p className="text-sm text-blue-600 font-medium">
                    {record.doctor?.specialization || 'Specialist'}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-gray-500 font-medium">Patient:</p>
                  <p className="text-sm text-gray-900 font-semibold">
                    {record.patient_name || 'Patient'}
                  </p>
                </div>
              </div>

              {/* Medical Details */}
              <div className="space-y-4 mb-4">
                {(record.disease_name || record.diagnosis) && (
                  <div className="bg-blue-50 rounded-lg p-3 border-l-4 border-blue-500">
                    <p className="text-xs font-bold text-blue-900 uppercase mb-1">
                      🔍 Disease / Condition
                    </p>
                    <p className="text-sm text-blue-900 font-semibold">
                      {record.disease_name || 'Diagnosis Information'}
                    </p>
                  </div>
                )}

                {record.diagnosis && (
                  <div className="bg-cyan-50 rounded-lg p-3 border-l-4 border-cyan-500">
                    <p className="text-xs font-bold text-cyan-900 uppercase mb-1">
                      📝 Diagnosis
                    </p>
                    <p className="text-sm text-cyan-900">{record.diagnosis}</p>
                  </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {record.prescription_text && (
                    <div className="bg-green-50 rounded-lg p-3 border-l-4 border-green-500">
                      <p className="text-xs font-bold text-green-900 uppercase mb-1">
                        💊 Prescription
                      </p>
                      <p className="text-sm text-green-900 font-semibold">
                        {record.prescription_text}
                      </p>
                      {record.dosage && (
                        <p className="text-xs text-green-700 mt-1">
                          Dosage: {record.dosage}
                        </p>
                      )}
                    </div>
                  )}

                  {record.follow_up_date && (
                    <div className="bg-orange-50 rounded-lg p-3 border-l-4 border-orange-500">
                      <p className="text-xs font-bold text-orange-900 uppercase mb-1">
                        📅 Follow-up Appointment
                      </p>
                      <p className="text-sm text-orange-900 font-semibold">
                        {formatDate(record.follow_up_date)}
                      </p>
                    </div>
                  )}
                </div>

                {record.notes && (
                  <div className="bg-gray-50 rounded-lg p-3 border-l-4 border-gray-400">
                    <p className="text-xs font-bold text-gray-700 uppercase mb-1">
                      📌 Clinical Notes
                    </p>
                    <p className="text-sm text-gray-700">{record.notes}</p>
                  </div>
                )}
              </div>

              {/* Footer */}
              <div className="flex justify-between items-center pt-4 border-t border-gray-200">
                <p className="text-xs text-gray-500">
                  Posted: {formatDate(record.created_at)}
                </p>
                <button 
                  onClick={() => downloadReport(record)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium cursor-pointer shadow-sm hover:shadow-md"
                  title="Download this medical report as a text file"
                >
                  📥 Download Report
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
            Your medical records from doctors will appear here after appointments and consultations.
          </p>
        </div>
      )}
    </div>
  );
}

