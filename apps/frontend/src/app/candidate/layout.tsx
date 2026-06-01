'use client';

import React from 'react';
import { CandidatePortalLayout } from '@/components/templates/CandidatePortalLayout';

export default function CandidatePortalLayout_({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <CandidatePortalLayout
      header={
        <div className="px-6 py-4 flex items-center justify-between">
          <h1 className="font-bold text-on-surface">NeuroHire Candidate Portal</h1>
          <button className="text-on-surface-variant hover:text-on-surface">Sign Out</button>
        </div>
      }
    >
      {children}
    </CandidatePortalLayout>
  );
}
