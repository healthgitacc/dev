import { Metadata } from 'next';
import { UsersPageClient } from './UsersPageClient';

export const metadata: Metadata = {
  title: 'Users | Hospital Management System',
  description: 'Manage system users (Admin only)',
};

export default function UsersPage() {
  return <UsersPageClient />;
}
