'use client';

import React from 'react';
import { InterviewScheduler } from '@/components/organisms/InterviewScheduler';

export default function CandidateDetailPage({ params }: { params: { id: string } }) {
  return (
    <div className="p-8 space-y-8">
      <h1 className="text-headline-lg font-bold text-on-surface">Candidate Profile</h1>
      <div className="p-8 bg-surface-container rounded-lg border border-outline-variant text-center text-on-surface-variant">
        Candidate detail content for ID: {params.id}
      </div>
      <InterviewScheduler candidateId={params.id} />
    </div>
  );
}
