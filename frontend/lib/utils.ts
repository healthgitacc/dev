import { format, parseISO } from 'date-fns';

/**
 * Format date string to readable format
 */
export const formatDate = (dateString: string, formatStr: string = 'PPP'): string => {
  try {
    return format(parseISO(dateString), formatStr);
  } catch {
    return dateString;
  }
};

/**
 * Format date and time
 */
export const formatDateTime = (dateString: string): string => {
  return formatDate(dateString, 'PPP p');
};

/**
 * Format date only
 */
export const formatDateOnly = (dateString: string): string => {
  return formatDate(dateString, 'MMM dd, yyyy');
};

/**
 * Format time only
 */
export const formatTimeOnly = (dateString: string): string => {
  return formatDate(dateString, 'HH:mm');
};

/**
 * Get status color class
 */
export const getStatusColor = (status: string): string => {
  const colorMap: Record<string, string> = {
    scheduled: 'bg-blue-100 text-blue-800',
    completed: 'bg-green-100 text-green-800',
    cancelled: 'bg-red-100 text-red-800',
    no_show: 'bg-yellow-100 text-yellow-800',
    rescheduled: 'bg-purple-100 text-purple-800',
    active: 'bg-green-100 text-green-800',
    inactive: 'bg-gray-100 text-gray-800',
  };
  return colorMap[status] || 'bg-gray-100 text-gray-800';
};

/**
 * Get role display name
 */
export const getRoleDisplayName = (role: string): string => {
  const roleMap: Record<string, string> = {
    admin: 'Administrator',
    doctor: 'Doctor',
    patient: 'Patient',
  };
  return roleMap[role] || role;
};

/**
 * Get role badge color
 */
export const getRoleBadgeColor = (role: string): string => {
  const colorMap: Record<string, string> = {
    admin: 'bg-red-100 text-red-800',
    doctor: 'bg-blue-100 text-blue-800',
    patient: 'bg-green-100 text-green-800',
  };
  return colorMap[role] || 'bg-gray-100 text-gray-800';
};

/**
 * Truncate text to specified length
 */
export const truncateText = (text: string, maxLength: number = 100): string => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

/**
 * Parse error response
 */
export const getErrorMessage = (error: unknown): string => {
  if (error instanceof Error) {
    return error.message;
  }
  if (typeof error === 'string') {
    return error;
  }
  if (error && typeof error === 'object' && 'detail' in error) {
    return String(error.detail);
  }
  return 'An error occurred';
};

/**
 * Check if email is valid
 */
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Generate initials from name
 */
export const getInitials = (name: string): string => {
  return name
    .split(' ')
    .map((part) => part[0])
    .join('')
    .toUpperCase()
    .substring(0, 2);
};

/**
 * Format blood group display
 */
export const formatBloodGroup = (bloodGroup: string | null): string => {
  return bloodGroup || 'Not specified';
};
