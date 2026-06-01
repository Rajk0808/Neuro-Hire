'use client';

import React from 'react';
import { JDEditorPanel } from '@/components/organisms/JDEditorPanel';

export default function NewJobPage() {
  return (
    <div className="p-8">
      <h1 className="text-headline-lg font-bold text-on-surface mb-6">Create New Requisition</h1>
      <JDEditorPanel />
    </div>
  );
}
