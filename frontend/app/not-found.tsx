import { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Page Not Found | Hospital Management System',
};

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-600 to-blue-800">
      <div className="text-center text-white max-w-md px-4">
        <h1 className="text-6xl font-bold mb-4">404</h1>
        <h2 className="text-2xl font-semibold mb-4">Page Not Found</h2>
        <p className="text-blue-100 mb-8">
          The page you are looking for doesn't exist or has been moved.
        </p>
        <Link
          href="/dashboard"
          className="inline-block px-8 py-3 bg-white text-blue-600 rounded-lg font-semibold hover:bg-blue-50 transition-colors"
        >
          Back to Dashboard
        </Link>
      </div>
    </div>
  );
}
