export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen flex flex-col lg:flex-row">
      {/* Left: Branding - hidden on small screens */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-slate-800 via-primary-900 to-slate-900 flex-col justify-between p-12 xl:p-16 text-white">
        <div>
          <h1 className="text-3xl xl:text-4xl font-bold tracking-tight">
            CareFlow
          </h1>
          <p className="text-primary-200 text-lg mt-2">
            Hospital Management &amp; Medical Records
          </p>
        </div>
        <div className="space-y-6">
          {[
            { title: 'Easy scheduling', desc: 'Book and manage appointments in one place', icon: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z' },
            { title: 'Secure records', desc: 'Your health data is protected and accessible', icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' },
            { title: 'Smart reminders', desc: 'SMS and in-app reminders so you never miss a visit', icon: 'M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9' },
          ].map((item) => (
            <div key={item.title} className="flex items-start gap-4">
              <div className="flex-shrink-0 w-12 h-12 rounded-xl bg-white/10 flex items-center justify-center">
                <svg className="w-6 h-6 text-primary-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={item.icon} />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-semibold">{item.title}</h3>
                <p className="text-slate-300 text-sm mt-0.5">{item.desc}</p>
              </div>
            </div>
          ))}
        </div>
        <p className="text-slate-400 text-sm">
          © {new Date().getFullYear()} CareFlow. All rights reserved.
        </p>
      </div>

      {/* Right: Form */}
      <div className="flex-1 flex items-center justify-center px-4 py-10 sm:px-6 lg:px-8 bg-slate-50">
        <div className="w-full max-w-md">
          <div className="lg:hidden text-center mb-8">
            <h1 className="text-2xl font-bold text-slate-900">CareFlow</h1>
            <p className="mt-1 text-slate-600 text-sm">Hospital Management</p>
          </div>
          <div className="card p-6 sm:p-8">
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}
