import { Metadata } from 'next';
import { ProfilePageClient } from './ProfilePageClient';

export const metadata: Metadata = {
  title: 'Change Password | Hospital Management System',
  description: 'Change your account password',
};

export default function ProfilePage() {
  return <ProfilePageClient />;
}
