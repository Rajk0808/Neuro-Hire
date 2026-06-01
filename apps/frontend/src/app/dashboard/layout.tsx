'use client';

import React from 'react';
import { DashboardLayout } from '@/components/templates/DashboardLayout';

// Sidebar component
const Sidebar = () => (
  <div className="p-6">
    <div className="flex items-center gap-2 mb-8">
      <div className="w-8 h-8 bg-primary rounded-lg" />
      <div>
        <h1 className="font-bold text-on-surface">NeuroHire</h1>
      </div>
    </div>

    <nav className="space-y-2">
      <a href="/dashboard" className="block px-4 py-2 bg-secondary-container text-on-secondary-container rounded-lg font-medium">
        Dashboard
      </a>
      <a href="/dashboard/jobs" className="block px-4 py-2 text-on-surface-variant hover:bg-surface-container rounded-lg">
        Jobs
      </a>
      <a href="/dashboard/candidates" className="block px-4 py-2 text-on-surface-variant hover:bg-surface-container rounded-lg">
        Candidates
      </a>
      <a href="/dashboard/interviews" className="block px-4 py-2 text-on-surface-variant hover:bg-surface-container rounded-lg">
        Interviews
      </a>
      <a href="/dashboard/analytics" className="block px-4 py-2 text-on-surface-variant hover:bg-surface-container rounded-lg">
        Intelligence
      </a>
    </nav>
  </div>
);

// Top bar component
const TopBar = () => (
  <div className="h-full flex items-center justify-between px-6">
    <input
      type="text"
      placeholder="Search..."
      className="px-4 py-2 bg-surface-container rounded-lg border border-outline-variant text-on-surface placeholder:text-on-surface-variant focus:outline-none"
    />
    <div className="flex items-center gap-4">
      <button className="text-on-surface-variant hover:text-on-surface">🔔</button>
      <button className="text-on-surface-variant hover:text-on-surface">⚙️</button>
    </div>
  </div>
);

export default function DashboardLayout_({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <DashboardLayout
      sidebar={<Sidebar />}
      topBar={<TopBar />}
    >
      {children}
    </DashboardLayout>
  );
}
