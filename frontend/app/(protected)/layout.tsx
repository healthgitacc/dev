import { Header } from '@/components/common/Header';
import { Sidebar } from '@/components/common/Sidebar';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';

export default function ProtectedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ProtectedRoute>
      <div className="flex min-h-screen bg-slate-50">
        <Sidebar />
        <div className="flex flex-1 flex-col min-w-0">
          <Header />
          <main className="flex-1 overflow-x-hidden">
            <div className="container-app py-6 sm:py-8 pl-14 sm:pl-6 lg:pl-8 animate-in">
              {children}
            </div>
          </main>
        </div>
      </div>
    </ProtectedRoute>
  );
}
