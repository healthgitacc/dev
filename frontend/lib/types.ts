/**
 * Application Types and Interfaces
 */

export type UserRole = 'admin' | 'doctor' | 'patient' | 'hospital_admin' | 'super_admin' | 'super_owner';
export type AppointmentStatus = 'scheduled' | 'completed' | 'cancelled' | 'no-show';
export type RecordStatus = 'active' | 'archived';

/**
 * User Types
 */
export interface User {
  id: number;
  name: string;
  email: string;
  phone: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Doctor extends User {
  specialization: string;
  license_number: string;
  profile_image?: string;
}

export interface Patient extends User {
  blood_group?: string;
  medical_history?: string;
  gender?: 'male' | 'female' | 'other';
  date_of_birth?: string;
  profile_image?: string;
}

export interface Hospital {
  id: number;
  name: string;
  email: string;
  phone?: string;
  address?: string;
  status: 'active' | 'inactive';
  created_at: string;
  updated_at: string;
}

/**
 * Authentication Types
 */
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  name: string;
  email: string;
  password: string;
  phone: string;
  role: UserRole;
  specialization?: string;
  license_number?: string;
  blood_group?: string;
  gender?: string;
  date_of_birth?: string;
}

export interface ChangePasswordData {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

/**
 * Appointment Types
 */
export interface Appointment {
  id: number;
  doctor_id: number;
  patient_id: number;
  appointment_date: string;
  appointment_time: string;
  status: AppointmentStatus;
  reason: string;
  notes?: string;
  reminder_sent: boolean;
  rescheduled_from?: number;
  created_at: string;
  updated_at: string;
  doctor?: Doctor;
  patient?: Patient;
}

export interface CreateAppointmentData {
  doctor_id: number;
  appointment_date: string;
  appointment_time: string;
  reason: string;
  notes?: string;
}

export interface RescheduleAppointmentData {
  appointment_date: string;
  appointment_time: string;
  reason?: string;
}

export interface AppointmentConflict {
  id: number;
  appointment_date: string;
  appointment_time: string;
  doctor_name: string;
}

/**
 * Medical Record Types
 */
export interface MedicalRecord {
  id: number;
  patient_id: number;
  doctor_id: number;
  diagnosis: string;
  treatment: string;
  prescription?: string;
  follow_up_date?: string;
  notes?: string;
  status: RecordStatus;
  created_at: string;
  updated_at: string;
  patient?: Patient;
  doctor?: Doctor;
}

export interface CreateMedicalRecordData {
  patient_id: number;
  diagnosis: string;
  treatment: string;
  prescription?: string;
  follow_up_date?: string;
  notes?: string;
}

/**
 * Pagination Types
 */
export interface PaginationParams {
  page?: number;
  page_size?: number;
  skip?: number;
  limit?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page?: number;
  page_size?: number;
  pages?: number;
}

/**
 * Filter Types
 */
export interface AppointmentFilters extends PaginationParams {
  status?: AppointmentStatus;
  doctor_id?: number;
  patient_id?: number;
  start_date?: string;
  end_date?: string;
}

export interface MedicalRecordFilters extends PaginationParams {
  patient_id?: number;
  doctor_id?: number;
  status?: RecordStatus;
}

export interface UserFilters extends PaginationParams {
  role?: UserRole;
  is_active?: boolean;
  search?: string;
}

export interface DoctorFilters extends PaginationParams {
  specialization?: string;
  search?: string;
}

export interface PatientFilters extends PaginationParams {
  blood_group?: string;
  gender?: string;
  search?: string;
}

/**
 * Dashboard Types
 */
export interface DashboardStats {
  total_users: number;
  total_doctors: number;
  total_patients: number;
  total_appointments: number;
  total_medical_records: number;
  appointments_today: number;
  appointments_this_week: number;
}

export interface UserStats {
  total_count: number;
  admin_count: number;
  doctor_count: number;
  patient_count: number;
}

/**
 * API Response Types
 */
export interface ApiError {
  detail: string | { [key: string]: string[] };
  status?: number;
}

export interface ApiResponse<T> {
  data?: T;
  error?: ApiError;
  message?: string;
}

/**
 * Form Response Types
 */
export interface FormError {
  field: string;
  message: string;
}

export interface FormResponse {
  success: boolean;
  message?: string;
  errors?: FormError[];
}
