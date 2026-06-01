'use client';

import React from 'react';

export default function JobDetailPage({ params }: { params: { id: string } }) {
  return (
    <div className="p-8">
      <h1 className="text-headline-lg font-bold text-on-surface mb-6">Job Details</h1>
      <div className="p-8 bg-surface-container rounded-lg border border-outline-variant text-center text-on-surface-variant">
        Job detail content for ID: {params.id}
      </div>
    </div>
  );
}
