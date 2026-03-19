'use client';

import { useEffect, useState } from 'react';
import { useAuthStore } from '@/lib/auth-store';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api';
import { API_ENDPOINTS } from '@/lib/constants';

interface Department {
  id: number;
  name: string;
  hospital_id: number;
}

interface CreateResponse {
  user_id: number;
  email: string;
  name: string;
  department_id: number;
  department_name: string;
  temporary_password: string;
}

export default function CreateDepartmentAdminPage() {
  const router = useRouter();
  const { user } = useAuthStore();
  const [departments, setDepartments] = useState<Department[]>([]);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [departmentId, setDepartmentId] = useState<number | ''>('');
  const [loading, setLoading] = useState(false);
  const [loadingDepts, setLoadingDepts] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<CreateResponse | null>(null);
  const [copied, setCopied] = useState(false);
  const [newDeptName, setNewDeptName] = useState('');
  const [creatingDept, setCreatingDept] = useState(false);
  const [deptError, setDeptError] = useState<string | null>(null);

  const fetchDepartments = async () => {
    try {
      setLoadingDepts(true);
      setError(null);
      const res = await apiClient.get<{ items: Department[] }>(API_ENDPOINTS.DEPARTMENTS);
      const items = Array.isArray(res.data?.items) ? res.data.items : (res.data as unknown as { items?: Department[] })?.items ?? [];
      setDepartments(items);
      if (items.length > 0) setDepartmentId(items[0].id);
    } catch (e) {
      setError('Failed to load departments');
      setDepartments([]);
    } finally {
      setLoadingDepts(false);
    }
  };

  useEffect(() => {
    if (user?.role !== 'hospital_admin') {
      router.replace('/dashboard');
      return;
    }
    fetchDepartments();
  }, [user?.role, router]);

  const handleCreateDepartment = async (e: React.FormEvent) => {
    e.preventDefault();
    const name = newDeptName.trim();
    if (!name) {
      setDeptError('Enter a department name');
      return;
    }
    setDeptError(null);
    setCreatingDept(true);
    try {
      await apiClient.post(API_ENDPOINTS.DEPARTMENTS, { name });
      setNewDeptName('');
      await fetchDepartments();
    } catch (err: unknown) {
      const res = err && typeof err === 'object' && 'response' in err
        ? (err as { response?: { data?: { detail?: string | { message?: string } } } }).response?.data?.detail
        : undefined;
      const msg = typeof res === 'string' ? res : res?.message ?? 'Failed to create department';
      setDeptError(msg);
    } finally {
      setCreatingDept(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !email.trim() || !departmentId) {
      setError('Name, email, and department are required');
      return;
    }
    setError(null);
    setResult(null);
    setLoading(true);
    try {
      const res = await apiClient.post<CreateResponse>(API_ENDPOINTS.CREATE_DEPARTMENT_ADMIN, {
        name: name.trim(),
        email: email.trim(),
        department_id: Number(departmentId),
        phone: phone.trim() || undefined,
      });
      setResult(res.data);
      setName('');
      setEmail('');
      setPhone('');
    } catch (err: unknown) {
      const msg =
        err && typeof err === 'object' && 'response' in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : 'Failed to create department admin';
      setError(typeof msg === 'string' ? msg : 'Failed to create department admin');
    } finally {
      setLoading(false);
    }
  };

  const copyPassword = () => {
    if (result?.temporary_password) {
      navigator.clipboard.writeText(result.temporary_password);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (user?.role !== 'hospital_admin') return null;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl sm:text-3xl font-bold text-slate-900">Create Department Admin</h1>
      <p className="text-slate-600">
        Create a new department admin (e.g. Ortho, Neuro, Uro). They will get a temporary password and can only manage their department.
      </p>

      {loadingDepts && <p className="text-slate-500">Loading departments...</p>}
      {!loadingDepts && departments.length === 0 && !error && (
        <div className="card p-6 border-primary-200 bg-primary-50/50">
          <h2 className="text-lg font-semibold text-primary-900 mb-2">Add your first department</h2>
          <p className="text-primary-800 text-sm mb-4">Create a department (e.g. Ortho, Neuro, Uro) for your hospital. Then you can create department admins for it.</p>
          <form onSubmit={handleCreateDepartment} className="flex flex-wrap gap-3 items-end">
            <div className="flex-1 min-w-[200px]">
              <label htmlFor="new-dept-name" className="block text-sm font-medium text-slate-700 mb-1">Department name</label>
              <input
                id="new-dept-name"
                type="text"
                value={newDeptName}
                onChange={(e) => setNewDeptName(e.target.value)}
                className="input-base"
                placeholder="e.g. Ortho, Neuro, Uro"
              />
            </div>
            <button type="submit" disabled={creatingDept || !newDeptName.trim()} className="btn-primary">
              {creatingDept ? 'Creating...' : 'Create department'}
            </button>
          </form>
          {deptError && <p className="text-red-600 text-sm mt-2">{deptError}</p>}
          <p className="text-slate-600 text-xs mt-3">Departments are created for your hospital. You can then assign department admins (e.g. Ortho, Cardio) to each department.</p>
        </div>
      )}
      {!loadingDepts && departments.length > 0 && (
        <div className="card p-4 flex flex-wrap gap-2 items-center">
          <span className="text-sm font-medium text-slate-700">Add another department:</span>
          <form onSubmit={handleCreateDepartment} className="flex flex-wrap gap-2 items-center">
            <input
              type="text"
              value={newDeptName}
              onChange={(e) => setNewDeptName(e.target.value)}
              className="input-base w-40"
              placeholder="e.g. Cardiology"
            />
            <button type="submit" disabled={creatingDept || !newDeptName.trim()} className="btn-secondary text-sm py-2">
              {creatingDept ? '...' : 'Add'}
            </button>
          </form>
          {deptError && <span className="text-red-600 text-sm">{deptError}</span>}
        </div>
      )}

      {error && (
        <div className="rounded-xl bg-red-50 border border-red-200 p-4">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {result && (
        <div className="card p-6 border-emerald-200 bg-emerald-50/50">
          <h2 className="text-lg font-semibold text-emerald-900 mb-2">Department admin created</h2>
          <p className="text-emerald-800 text-sm mb-2">{result.name} ({result.email}) – {result.department_name}</p>
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-sm font-medium text-slate-700">Temporary password:</span>
            <code className="px-3 py-1.5 bg-white border border-slate-200 rounded-lg font-mono text-sm">{result.temporary_password}</code>
            <button type="button" onClick={copyPassword} className="btn-secondary text-sm py-1.5">
              {copied ? 'Copied!' : 'Copy'}
            </button>
          </div>
          <p className="text-xs text-slate-600 mt-2">Share this password with the user once. They should change it after first login.</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="card p-6 max-w-lg space-y-4">
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-slate-700 mb-1.5">Name</label>
          <input
            id="name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="input-base"
            placeholder="Full name"
            required
          />
        </div>
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-slate-700 mb-1.5">Email</label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="input-base"
            placeholder="email@example.com"
            required
          />
        </div>
        <div>
          <label htmlFor="phone" className="block text-sm font-medium text-slate-700 mb-1.5">Phone (optional)</label>
          <input
            id="phone"
            type="text"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            className="input-base"
            placeholder="+91..."
          />
        </div>
        <div>
          <label htmlFor="department" className="block text-sm font-medium text-slate-700 mb-1.5">Department</label>
          <select
            id="department"
            value={departmentId}
            onChange={(e) => setDepartmentId(e.target.value ? Number(e.target.value) : '')}
            className="input-base"
            required
          >
            <option value="">Select department</option>
            {departments.map((d) => (
              <option key={d.id} value={d.id}>{d.name}</option>
            ))}
          </select>
        </div>
        <button type="submit" disabled={loading || departments.length === 0} className="btn-primary">
          {loading ? 'Creating...' : 'Create Department Admin'}
        </button>
      </form>
    </div>
  );
}
