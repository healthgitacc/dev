/**
 * Zod Validation Schemas
 */

import { z } from 'zod';
import { VALIDATION, BLOOD_GROUPS } from './constants';

/**
 * Auth Schemas
 */
export const loginSchema = z.object({
  email: z
    .string()
    .email('Invalid email format')
    .max(VALIDATION.MAX_EMAIL_LENGTH, 'Email too long'),
  password: z
    .string()
    .min(1, 'Password is required')
    .min(VALIDATION.MIN_PASSWORD_LENGTH, `Password must be at least ${VALIDATION.MIN_PASSWORD_LENGTH} characters`),
});

export type LoginFormData = z.infer<typeof loginSchema>;

export const registerSchema = z
  .object({
    name: z
      .string()
      .min(1, 'Name is required')
      .max(VALIDATION.MAX_NAME_LENGTH, 'Name too long'),
    email: z
      .string()
      .email('Invalid email format')
      .max(VALIDATION.MAX_EMAIL_LENGTH, 'Email too long'),
    phone: z
      .string()
      .min(10, 'Phone number must be at least 10 digits')
      .max(20, 'Phone number too long')
      .regex(/^[0-9+\-\s()]*$/, 'Invalid phone number format'),
    password: z
      .string()
      .min(VALIDATION.MIN_PASSWORD_LENGTH, `Password must be at least ${VALIDATION.MIN_PASSWORD_LENGTH} characters`)
      .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
      .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
      .regex(/[0-9]/, 'Password must contain at least one number'),
    confirmPassword: z.string(),
    role: z.enum(['admin', 'doctor', 'patient']),
    specialization: z.string().optional(),
    license_number: z.string().optional(),
    blood_group: z.enum(BLOOD_GROUPS).optional(),
    gender: z.enum(['male', 'female', 'other']).optional(),
    date_of_birth: z.string().optional(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: 'Passwords do not match',
    path: ['confirmPassword'],
  })
  .refine((data) => (data.role === 'doctor' ? !!data.specialization && !!data.license_number : true), {
    message: 'Doctors must provide specialization and license number',
    path: ['specialization'],
  });

export type RegisterFormData = z.infer<typeof registerSchema>;

export const changePasswordSchema = z
  .object({
    current_password: z
      .string()
      .min(1, 'Current password is required'),
    new_password: z
      .string()
      .min(VALIDATION.MIN_PASSWORD_LENGTH, `Password must be at least ${VALIDATION.MIN_PASSWORD_LENGTH} characters`)
      .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
      .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
      .regex(/[0-9]/, 'Password must contain at least one number'),
    confirm_password: z.string(),
  })
  .refine((data) => data.new_password === data.confirm_password, {
    message: 'Passwords do not match',
    path: ['confirm_password'],
  })
  .refine((data) => data.current_password !== data.new_password, {
    message: 'New password must be different from current password',
    path: ['new_password'],
  });

export type ChangePasswordFormData = z.infer<typeof changePasswordSchema>;

/**
 * Profile Schemas
 */
export const profileSchema = z.object({
  name: z
    .string()
    .min(1, 'Name is required')
    .max(VALIDATION.MAX_NAME_LENGTH, 'Name too long'),
  email: z
    .string()
    .email('Invalid email format')
    .max(VALIDATION.MAX_EMAIL_LENGTH, 'Email too long'),
  phone: z
    .string()
    .min(10, 'Phone number must be at least 10 digits')
    .max(20, 'Phone number too long')
    .regex(/^[0-9+\-\s()]*$/, 'Invalid phone number format'),
});

export type ProfileFormData = z.infer<typeof profileSchema>;

export const doctorProfileSchema = profileSchema.extend({
  specialization: z
    .string()
    .min(1, 'Specialization is required'),
  license_number: z
    .string()
    .min(1, 'License number is required'),
});

export type DoctorProfileFormData = z.infer<typeof doctorProfileSchema>;

export const patientProfileSchema = profileSchema.extend({
  blood_group: z
    .enum(BLOOD_GROUPS)
    .optional(),
  gender: z
    .enum(['male', 'female', 'other'])
    .optional(),
  date_of_birth: z
    .string()
    .optional(),
  medical_history: z
    .string()
    .max(2000, 'Medical history too long')
    .optional(),
});

export type PatientProfileFormData = z.infer<typeof patientProfileSchema>;

/**
 * Appointment Schemas
 */
export const appointmentSchema = z.object({
  doctor_id: z
    .number()
    .min(1, 'Doctor is required'),
  appointment_date: z
    .string()
    .min(1, 'Date is required'),
  appointment_time: z
    .string()
    .min(1, 'Time is required')
    .regex(/^([0-1][0-9]|2[0-3]):[0-5][0-9]$/, 'Invalid time format'),
  reason: z
    .string()
    .min(1, 'Reason is required')
    .max(VALIDATION.MAX_REASON_LENGTH, 'Reason too long'),
  notes: z
    .string()
    .max(VALIDATION.MAX_NOTES_LENGTH, 'Notes too long')
    .optional(),
});

export type AppointmentFormData = z.infer<typeof appointmentSchema>;

export const rescheduleAppointmentSchema = z.object({
  appointment_date: z
    .string()
    .min(1, 'Date is required'),
  appointment_time: z
    .string()
    .min(1, 'Time is required')
    .regex(/^([0-1][0-9]|2[0-3]):[0-5][0-9]$/, 'Invalid time format'),
  reason: z
    .string()
    .max(VALIDATION.MAX_REASON_LENGTH, 'Reason too long')
    .optional(),
});

export type RescheduleAppointmentFormData = z.infer<typeof rescheduleAppointmentSchema>;

/**
 * Medical Record Schemas
 */
export const medicalRecordSchema = z.object({
  patient_id: z
    .number()
    .min(1, 'Patient is required'),
  diagnosis: z
    .string()
    .min(1, 'Diagnosis is required')
    .max(VALIDATION.MAX_REASON_LENGTH, 'Diagnosis too long'),
  treatment: z
    .string()
    .min(1, 'Treatment is required')
    .max(VALIDATION.MAX_NOTES_LENGTH, 'Treatment too long'),
  prescription: z
    .string()
    .max(VALIDATION.MAX_NOTES_LENGTH, 'Prescription too long')
    .optional(),
  follow_up_date: z
    .string()
    .optional(),
  notes: z
    .string()
    .max(VALIDATION.MAX_NOTES_LENGTH, 'Notes too long')
    .optional(),
});

export type MedicalRecordFormData = z.infer<typeof medicalRecordSchema>;

/**
 * Search and Filter Schemas
 */
export const appointmentFilterSchema = z.object({
  status: z
    .enum(['scheduled', 'completed', 'cancelled', 'no-show'])
    .optional(),
  doctor_id: z
    .number()
    .optional(),
  patient_id: z
    .number()
    .optional(),
  start_date: z
    .string()
    .optional(),
  end_date: z
    .string()
    .optional(),
  page: z
    .number()
    .min(1)
    .optional(),
  page_size: z
    .number()
    .min(1)
    .max(100)
    .optional(),
});

export type AppointmentFilterFormData = z.infer<typeof appointmentFilterSchema>;

export const searchSchema = z.object({
  query: z
    .string()
    .min(1, 'Search query is required')
    .max(100, 'Search query too long'),
});

export type SearchFormData = z.infer<typeof searchSchema>;

/**
 * Date Range Schema (for reports, filters, etc.)
 */
export const dateRangeSchema = z
  .object({
    start_date: z
      .string()
      .min(1, 'Start date is required'),
    end_date: z
      .string()
      .min(1, 'End date is required'),
  })
  .refine((data) => new Date(data.start_date) <= new Date(data.end_date), {
    message: 'End date must be after start date',
    path: ['end_date'],
  });

export type DateRangeFormData = z.infer<typeof dateRangeSchema>;

/**
 * Pagination Schema
 */
export const paginationSchema = z.object({
  page: z
    .number()
    .min(1, 'Page must be at least 1')
    .default(1),
  page_size: z
    .number()
    .min(1, 'Page size must be at least 1')
    .max(100, 'Page size cannot exceed 100')
    .default(10),
});

export type PaginationFormData = z.infer<typeof paginationSchema>;
