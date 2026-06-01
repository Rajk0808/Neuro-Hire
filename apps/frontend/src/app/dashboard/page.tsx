'use client';

import React from 'react';

export default function DashboardPage() {
  return (
    <div className="p-8 space-y-8">
      <div>
        <h1 className="text-headline-lg font-bold text-on-surface mb-2">Dashboard</h1>
        <p className="text-on-surface-variant">Welcome to NeuroHire Intelligence</p>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-4 gap-6">
        {[
          { label: 'Open Roles', value: '42', icon: '📋' },
          { label: 'Candidates', value: '1,284', icon: '👥' },
          { label: 'Avg Time-to-Hire', value: '14.5d', icon: '⏱️' },
          { label: 'Bias Score', value: '98.2', icon: '✓' },
        ].map((metric) => (
          <div
            key={metric.label}
            className="p-6 bg-surface-container rounded-lg border border-outline-variant"
          >
            <div className="text-3xl mb-2">{metric.icon}</div>
            <p className="text-sm text-on-surface-variant mb-1">{metric.label}</p>
            <p className="text-headline-md font-bold text-on-surface">{metric.value}</p>
          </div>
        ))}
      </div>

      {/* Placeholder for future content */}
      <div className="p-8 bg-surface-container rounded-lg border border-outline-variant text-center text-on-surface-variant">
        <p>Main dashboard content goes here</p>
      </div>
    </div>
  );
}
