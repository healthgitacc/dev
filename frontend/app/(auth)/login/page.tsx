import { Metadata } from 'next';
import { LoginForm } from '@/components/forms/LoginForm';

export const metadata: Metadata = {
  title: 'Login | Hospital Management System',
  description: 'Sign in to your hospital account',
};

export default function LoginPage() {
  return (
    <div>
      <div className="mb-6">
        <h2 className="text-xl sm:text-2xl font-bold text-slate-900">Welcome back</h2>
        <p className="mt-1.5 text-slate-600 text-sm">
          Sign in to your account to continue
        </p>
      </div>
      <LoginForm />
    </div>
  );
}
