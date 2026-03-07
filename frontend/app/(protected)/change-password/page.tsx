import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Change Password | Hospital Management System',
  description: 'Change your account password',
};

export default function ChangePasswordPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Change Password</h2>
          <p className="text-gray-600">Update your account password</p>
        </div>

        <form className="bg-white rounded-lg shadow-sm p-8 border border-gray-200 space-y-6">
          <div>
            <label htmlFor="current" className="block text-sm font-medium text-gray-700 mb-2">
              Current Password
            </label>
            <input
              id="current"
              type="password"
              placeholder="••••••••"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent"
            />
          </div>

          <div>
            <label htmlFor="new" className="block text-sm font-medium text-gray-700 mb-2">
              New Password
            </label>
            <input
              id="new"
              type="password"
              placeholder="••••••••"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent"
            />
          </div>

          <div>
            <label htmlFor="confirm" className="block text-sm font-medium text-gray-700 mb-2">
              Confirm Password
            </label>
            <input
              id="confirm"
              type="password"
              placeholder="••••••••"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent"
            />
          </div>

          <button
            type="submit"
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 transition-colors"
          >
            Update Password
          </button>
        </form>
      </div>
    </div>
  );
}
