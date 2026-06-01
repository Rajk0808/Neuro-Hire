'use client';

import React from 'react';

export default function InterviewCompanionPage({ params }: { params: { token: string } }) {
  return (
    <div>
      <h1 className="text-headline-lg font-bold text-on-surface mb-4">Interview Companion Chat</h1>
      <div className="p-8 bg-surface-container rounded-lg border border-outline-variant min-h-96">
        <p className="text-on-surface-variant text-center">
          Chat interface for interview token: {params.token}
        </p>
      </div>
    </div>
  );
}
