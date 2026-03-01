import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Admin Settings | Hospital Management System',
  description: 'System administration settings',
};

export default function AdminSettingsPage() {
  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Admin Settings</h1>
      
      {/* Settings Sections */}
      <div className="space-y-6">
        {/* General Settings */}
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">General Settings</h2>
          <form className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Hospital Name</label>
              <input
                type="text"
                placeholder="Hospital name"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Email Address</label>
              <input
                type="email"
                placeholder="hospital@example.com"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent"
              />
            </div>
            <button
              type="submit"
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Save Changes
            </button>
          </form>
        </div>

        {/* System Status */}
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">System Status</h2>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-gray-700">Database</span>
              <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">Connected</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-700">API Server</span>
              <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">Running</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-700">Email Service</span>
              <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-medium">Configured</span>
            </div>
          </div>
        </div>

        {/* Backup & Maintenance */}
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Backup & Maintenance</h2>
          <div className="space-y-3">
            <button className="w-full px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium">
              Backup Database
            </button>
            <button className="w-full px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium">
              View Logs
            </button>
            <button className="w-full px-4 py-2 border border-red-300 text-red-700 rounded-lg hover:bg-red-50 transition-colors text-sm font-medium">
              Clear Cache
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
