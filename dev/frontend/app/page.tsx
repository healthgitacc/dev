import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Hospital Management System',
  description: 'Welcome to Hospital Appointment & Medical Record Management System',
};

export default function Home() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-600 to-blue-800">
      <div className="text-center text-white max-w-2xl px-4">
        <h1 className="text-5xl font-bold mb-6">
          🏥 Hospital Management System
        </h1>
        <p className="text-xl mb-8 text-blue-100">
          Efficiently manage appointments and medical records online
        </p>
        <div className="flex gap-4 justify-center flex-wrap">
          <a
            href="/login"
            className="px-8 py-3 bg-white text-blue-600 rounded-lg font-semibold hover:bg-blue-50 transition-colors"
          >
            Sign In
          </a>
          <a
            href="/register"
            className="px-8 py-3 bg-blue-500 text-white rounded-lg font-semibold hover:bg-blue-400 transition-colors border-2 border-white"
          >
            Create Account
          </a>
        </div>
      </div>
    </div>
  );
}
