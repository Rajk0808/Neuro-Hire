'use client';

export default function DashboardPage() {
  const stats = [
    { label: 'Open Roles', value: '42', trend: '+12%' },
    { label: 'Candidates', value: '1,284', trend: '+8%' },
    { label: 'Time-to-Hire', value: '14.5 days', trend: '-5%' },
    { label: 'Bias Score', value: '98.2', trend: '+2%' },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-on-background">Dashboard</h1>
        <p className="text-on-surface-variant">Welcome to your recruitment command center</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, idx) => (
          <div
            key={idx}
            className="p-6 rounded-lg bg-surface-container border border-outline-variant hover:border-outline transition-colors"
          >
            <p className="text-sm text-on-surface-variant mb-2">{stat.label}</p>
            <div className="flex items-end justify-between">
              <p className="text-3xl font-bold text-on-background">{stat.value}</p>
              <span className="text-sm font-medium text-primary">{stat.trend}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Content Areas */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Placeholder for jobs */}
        <div className="lg:col-span-2 p-6 rounded-lg bg-surface-container border border-outline-variant">
          <h2 className="text-xl font-bold text-on-background mb-4">Recent Jobs</h2>
          <p className="text-on-surface-variant">Job listings will appear here</p>
        </div>

        {/* Placeholder for activity */}
        <div className="p-6 rounded-lg bg-surface-container border border-outline-variant">
          <h2 className="text-xl font-bold text-on-background mb-4">Activity</h2>
          <p className="text-on-surface-variant">Recent activity will appear here</p>
        </div>
      </div>
    </div>
  );
}
