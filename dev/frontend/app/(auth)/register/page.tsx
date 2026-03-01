import { Metadata } from 'next';
import { RegisterForm } from '@/components/forms/RegisterForm';

export const metadata: Metadata = {
  title: 'Register | Hospital Management System',
  description: 'Create a new hospital account',
};

export default function RegisterPage() {
  return (
    <div>
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900">Create account</h2>
        <p className="mt-2 text-gray-600">
          Join our hospital system to book appointments and manage your health records
        </p>
      </div>

      <RegisterForm />
    </div>
  );
}
