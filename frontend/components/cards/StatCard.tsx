import Link from 'next/link';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: string;
  trend?: { value: number; isPositive: boolean };
  description?: string;
  href?: string;
}

export function StatCard({ title, value, icon, trend, description, href }: StatCardProps) {
  const content = (
    <div className="card p-5 sm:p-6 flex items-start justify-between gap-4 group hover:shadow-soft transition-all duration-250">
      <div className="min-w-0 flex-1">
        <p className="text-sm font-medium text-slate-500">{title}</p>
        <p className="mt-2 flex flex-wrap items-baseline gap-2">
          <span className="text-2xl sm:text-3xl font-bold text-slate-900 tabular-nums">{value}</span>
          {trend && (
            <span className={`text-sm font-medium ${trend.isPositive ? 'text-emerald-600' : 'text-red-600'}`}>
              {trend.isPositive ? '↑' : '↓'} {trend.value}%
            </span>
          )}
        </p>
        {description && <p className="mt-1 text-xs text-slate-400">{description}</p>}
      </div>
      <div className="flex-shrink-0 w-12 h-12 rounded-xl bg-primary-50 text-primary-600 flex items-center justify-center text-2xl group-hover:bg-primary-100 transition-colors duration-200">
        {icon}
      </div>
    </div>
  );

  if (href) {
    return <Link href={href} className="block">{content}</Link>;
  }
  return content;
}
