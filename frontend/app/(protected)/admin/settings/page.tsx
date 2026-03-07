import { Metadata } from 'next';
import AdminSettingsClient from './AdminSettingsClient';

export const metadata: Metadata = {
  title: 'Admin Settings | Hospital Management System',
  description: 'System administration settings',
};

export default function AdminSettingsPage() {
  return <AdminSettingsClient />;
}
