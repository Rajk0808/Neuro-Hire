'use client';

import React, { useState } from 'react';
import { Job } from '@/types/job';

interface Column {
  id: string;
  title: string;
}

interface Card {
  id: string;
  columnId: string;
  title: string;
  data: Job;
}

interface PipelineKanbanProps {
  jobs: Job[];
}

export const PipelineKanban: React.FC<PipelineKanbanProps> = ({ jobs }) => {
  const columns: Column[] = [
    { id: 'draft', title: 'Draft' },
    { id: 'open', title: 'Open' },
    { id: 'screening', title: 'Screening' },
    { id: 'interviewing', title: 'Interviewing' },
    { id: 'closed', title: 'Closed' },
  ];

  return (
    <div className="flex gap-4 overflow-x-auto pb-4">
      {columns.map((column) => (
        <div key={column.id} className="flex-shrink-0 w-80">
          <div className="bg-surface-container-low rounded-lg p-4 min-h-96">
            <h3 className="font-semibold text-on-surface mb-4">{column.title}</h3>
            <div className="space-y-3">
              {jobs
                .filter((job) => job.status === column.id)
                .map((job) => (
                  <div key={job.id} className="p-3 bg-surface-container rounded-lg border border-outline-variant hover:border-primary/50 transition-all cursor-move">
                    <h4 className="font-medium text-on-surface text-sm mb-1">{job.title}</h4>
                    <p className="text-xs text-on-surface-variant">{job.applications_count} applications</p>
                  </div>
                ))}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};
