import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Users | Hospital Management System',
  description: 'Manage system users (Admin only)',
};

export default function UsersPage() {
  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Users</h1>
      
      {/* Search and Filter */}
      <div className="mb-6 bg-white rounded-lg shadow-sm p-6 border border-gray-200">
        <div className="flex gap-4">
          <input
            type="text"
            placeholder="Search users..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent"
          />
          <select className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent">
            <option>All Roles</option>
            <option>Admin</option>
            <option>Doctor</option>
            <option>Patient</option>
          </select>
          <button className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium">
            Add User
          </button>
        </div>
      </div>

      {/* Users Table */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Name</th>
              <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Email</th>
              <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Role</th>
              <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Status</th>
              <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            <tr className="hover:bg-gray-50">
              <td className="px-6 py-4 text-sm text-gray-900">Admin User</td>
              <td className="px-6 py-4 text-sm text-gray-600">admin@example.com</td>
              <td className="px-6 py-4 text-sm">
                <span className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-xs font-medium">Admin</span>
              </td>
              <td className="px-6 py-4 text-sm">
                <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">Active</span>
              </td>
              <td className="px-6 py-4 text-sm space-x-2">
                <button className="text-blue-600 hover:text-blue-700">View</button>
                <button className="text-gray-600 hover:text-gray-700">Edit</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
