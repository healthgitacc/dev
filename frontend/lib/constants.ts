/**
 * Application Constants
 */

/**
 * User Roles
 */
export const USER_ROLES = {
  ADMIN: 'admin',
  DOCTOR: 'doctor',
  PATIENT: 'patient',
} as const;

export const ROLE_LABELS: Record<string, string> = {
  admin: 'Administrator',
  doctor: 'Doctor',
  patient: 'Patient',
};

export const ROLE_COLORS: Record<string, string> = {
  admin: 'bg-red-100 text-red-800',
  doctor: 'bg-blue-100 text-blue-800',
  patient: 'bg-green-100 text-green-800',
};

/**
 * Appointment Statuses
 */
export const APPOINTMENT_STATUS = {
  SCHEDULED: 'scheduled',
  COMPLETED: 'completed',
  CANCELLED: 'cancelled',
  NO_SHOW: 'no-show',
} as const;

export const APPOINTMENT_STATUS_LABELS: Record<string, string> = {
  scheduled: 'Scheduled',
  completed: 'Completed',
  cancelled: 'Cancelled',
  'no-show': 'No Show',
};

export const APPOINTMENT_STATUS_COLORS: Record<string, string> = {
  scheduled: 'bg-blue-100 text-blue-800',
  completed: 'bg-green-100 text-green-800',
  cancelled: 'bg-red-100 text-red-800',
  'no-show': 'bg-yellow-100 text-yellow-800',
};

/**
 * Medical Record Status
 */
export const RECORD_STATUS = {
  ACTIVE: 'active',
  ARCHIVED: 'archived',
} as const;

/**
 * Gender Options
 */
export const GENDER_OPTIONS = [
  { value: 'male', label: 'Male' },
  { value: 'female', label: 'Female' },
  { value: 'other', label: 'Other' },
] as const;

/**
 * Blood Groups
 */
export const BLOOD_GROUPS = [
  'O+',
  'O-',
  'A+',
  'A-',
  'B+',
  'B-',
  'AB+',
  'AB-',
] as const;

/**
 * Specializations
 */
export const SPECIALIZATIONS = [
  'Cardiology',
  'Dermatology',
  'Neurology',
  'Orthopedics',
  'Pediatrics',
  'Psychiatry',
  'Oncology',
  'Gastroenterology',
  'Pulmonology',
  'Urology',
  'Ophthalmology',
  'Otolaryngology',
  'Rheumatology',
  'Nephrology',
  'Endocrinology',
  'Internal Medicine',
  'General Surgery',
  'Emergency Medicine',
] as const;

/**
 * API Endpoints
 */
export const API_ENDPOINTS = {
  // Auth
  AUTH_REGISTER: '/api/auth/register',
  AUTH_LOGIN: '/api/auth/login',
  AUTH_CHANGE_PASSWORD: '/api/auth/change-password',
  AUTH_ME: '/api/auth/me',

  // Users
  USERS: '/api/users',
  USER_BY_ID: (id: number) => `/api/users/${id}`,
  USER_STATS: '/api/users/stats',
  USER_ACTIVATE: (id: number) => `/api/users/${id}/activate`,
  USER_DEACTIVATE: (id: number) => `/api/users/${id}/deactivate`,

  // Doctors
  DOCTORS: '/api/doctors',
  DOCTOR_BY_ID: (id: number) => `/api/doctors/${id}`,
  DOCTOR_BY_SPECIALIZATION: (specialization: string) =>
    `/api/doctors/specialization/${specialization}`,

  // Patients
  PATIENTS: '/api/patients',
  PATIENT_BY_ID: (id: number) => `/api/patients/${id}`,
  PATIENT_BY_BLOOD_GROUP: (bloodGroup: string) =>
    `/api/patients/blood-group/${bloodGroup}`,
  PATIENT_BY_GENDER: (gender: string) => `/api/patients/gender/${gender}`,

  // Appointments
  APPOINTMENTS: '/api/appointments',
  APPOINTMENT_BY_ID: (id: number) => `/api/appointments/${id}`,
  APPOINTMENT_RESCHEDULE: (id: number) => `/api/appointments/${id}/reschedule`,
  APPOINTMENT_CANCEL: (id: number) => `/api/appointments/${id}`,
  APPOINTMENT_REMINDERS: '/api/appointments/reminders',

  // Medical Records
  MEDICAL_RECORDS: '/api/medical-records',
  MEDICAL_RECORD_BY_ID: (id: number) => `/api/medical-records/${id}`,
  MEDICAL_RECORDS_BY_PATIENT: (patientId: number) =>
    `/api/medical-records?patient_id=${patientId}`,
} as const;

/**
 * Pagination
 */
export const DEFAULT_PAGE_SIZE = 10;
export const PAGE_SIZE_OPTIONS = [10, 25, 50, 100];

/**
 * Time Format
 */
export const TIME_FORMAT = 'HH:mm';
export const DATE_FORMAT = 'yyyy-MM-dd';
export const DATETIME_FORMAT = 'yyyy-MM-dd HH:mm';
export const DISPLAY_DATE_FORMAT = 'MMMM d, yyyy';
export const DISPLAY_DATETIME_FORMAT = 'MMMM d, yyyy h:mm a';

/**
 * Appointment Hours
 */
export const APPOINTMENT_START_HOUR = 8;
export const APPOINTMENT_END_HOUR = 18;
export const APPOINTMENT_DURATION_MINUTES = 30;

export const APPOINTMENT_HOURS = Array.from(
  { length: APPOINTMENT_END_HOUR - APPOINTMENT_START_HOUR },
  (_, i) => {
    const hour = APPOINTMENT_START_HOUR + i;
    return `${String(hour).padStart(2, '0')}:00`;
  }
);

/**
 * Navigation
 */
export const NAV_ITEMS_PATIENT = [
  { label: 'Dashboard', href: '/dashboard', icon: 'home' },
  { label: 'Appointments', href: '/appointments', icon: 'calendar' },
  { label: 'Medical Records', href: '/medical-records', icon: 'document' },
  { label: 'Doctors', href: '/doctors', icon: 'users' },
  { label: 'Profile', href: '/profile', icon: 'user' },
];

export const NAV_ITEMS_DOCTOR = [
  { label: 'Dashboard', href: '/dashboard', icon: 'home' },
  { label: 'Appointments', href: '/appointments', icon: 'calendar' },
  { label: 'Patients', href: '/patients', icon: 'users' },
  { label: 'Medical Records', href: '/medical-records', icon: 'document' },
  { label: 'Profile', href: '/profile', icon: 'user' },
];

export const NAV_ITEMS_ADMIN = [
  { label: 'Dashboard', href: '/dashboard', icon: 'home' },
  { label: 'Users', href: '/users', icon: 'users' },
  { label: 'Doctors', href: '/admin/doctors', icon: 'users' },
  { label: 'Patients', href: '/admin/patients', icon: 'users' },
  { label: 'Appointments', href: '/admin/appointments', icon: 'calendar' },
  { label: 'Medical Records', href: '/admin/records', icon: 'document' },
  { label: 'Reports', href: '/admin/reports', icon: 'chart' },
  { label: 'Settings', href: '/admin/settings', icon: 'settings' },
];

/**
 * Error Messages
 */
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your connection.',
  UNAUTHORIZED: 'Unauthorized. Please log in again.',
  FORBIDDEN: 'You do not have permission to access this resource.',
  NOT_FOUND: 'Resource not found.',
  SERVER_ERROR: 'Server error. Please try again later.',
  FORM_VALIDATION: 'Please correct the errors below.',
  APPOINTMENT_CONFLICT: 'You already have an appointment at this time.',
  INVALID_CREDENTIALS: 'Invalid email or password.',
  EMAIL_EXISTS: 'Email already registered.',
  REQUIRED_FIELD: 'This field is required.',
} as const;

/**
 * Success Messages
 */
export const SUCCESS_MESSAGES = {
  LOGIN_SUCCESS: 'Login successful!',
  REGISTER_SUCCESS: 'Registration successful! Please log in.',
  LOGOUT_SUCCESS: 'Logged out successfully.',
  PROFILE_UPDATED: 'Profile updated successfully.',
  PASSWORD_CHANGED: 'Password changed successfully.',
  APPOINTMENT_CREATED: 'Appointment created successfully!',
  APPOINTMENT_UPDATED: 'Appointment updated successfully.',
  APPOINTMENT_CANCELLED: 'Appointment cancelled successfully.',
  APPOINTMENT_RESCHEDULED: 'Appointment rescheduled successfully.',
  RECORD_CREATED: 'Medical record created successfully.',
  RECORD_UPDATED: 'Medical record updated successfully.',
  RECORD_DELETED: 'Medical record deleted successfully.',
  USER_ACTIVATED: 'User activated successfully.',
  USER_DEACTIVATED: 'User deactivated successfully.',
} as const;

/**
 * Validation Rules
 */
export const VALIDATION = {
  MIN_PASSWORD_LENGTH: 8,
  MAX_NAME_LENGTH: 100,
  MAX_EMAIL_LENGTH: 255,
  MAX_PHONE_LENGTH: 20,
  MAX_REASON_LENGTH: 500,
  MAX_NOTES_LENGTH: 2000,
} as const;

/**
 * Page Titles
 */
export const PAGE_TITLES = {
  LOGIN: 'Login',
  REGISTER: 'Register',
  DASHBOARD: 'Dashboard',
  APPOINTMENTS: 'Appointments',
  PROFILE: 'Profile',
  CHANGE_PASSWORD: 'Change Password',
  MEDICAL_RECORDS: 'Medical Records',
  DOCTORS: 'Doctors',
  PATIENTS: 'Patients',
  USERS: 'Users',
  ADMIN: 'Administration',
} as const;

/**
 * Cookie Configuration
 */
export const COOKIE_CONFIG = {
  TOKEN_KEY: 'hospital_auth_token',
  USER_KEY: 'hospital_auth_user',
  TOKEN_EXPIRY_DAYS: 1,
} as const;

/**
 * Local Storage Keys
 */
export const STORAGE_KEYS = {
  USER: 'hospital_user',
  PREFERENCES: 'hospital_preferences',
  RECENT_SEARCHES: 'hospital_recent_searches',
} as const;
