'use client';

import React from 'react';
import { Job } from '@/types/job';
import { Badge } from '@/components/atoms/Badge';
import { formatSalary } from '@/lib/utils';

interface JobCardProps {
  job: Job;
  onClick?: () => void;
}

export const JobCard: React.FC<JobCardProps> = ({ job, onClick }) => {
  return (
    <div
      onClick={onClick}
      className="p-4 bg-surface-container rounded-lg border border-outline-variant hover:border-primary/50 transition-all cursor-pointer"
    >
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="font-semibold text-on-surface">{job.title}</h3>
          <p className="text-sm text-on-surface-variant">{job.department}</p>
        </div>
        <Badge variant="success">DEI: {job.dei_score}</Badge>
      </div>

      <p className="text-sm text-on-surface-variant mb-3">{job.location}</p>

      <div className="mb-3">
        <p className="text-sm font-medium text-on-surface">
          {formatSalary(job.salary_min, job.salary_max, job.currency)}
        </p>
      </div>

      <div className="flex flex-wrap gap-1 mb-3">
        {job.required_skills.slice(0, 3).map((skill) => (
          <Badge key={skill} variant="info">
            {skill}
          </Badge>
        ))}
        {job.required_skills.length > 3 && (
          <Badge variant="default">+{job.required_skills.length - 3}</Badge>
        )}
      </div>

      <div className="flex items-center justify-between text-xs text-on-surface-variant pt-3 border-t border-outline-variant">
        <span>{job.applications_count} applications</span>
        <Badge variant="success">{job.status}</Badge>
      </div>
    </div>
  );
};
