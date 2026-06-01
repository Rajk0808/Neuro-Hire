'use client';

import React from 'react';
import { Button } from '@/components/atoms/Button';

interface InterviewSchedulerProps {
  candidateId?: string;
  onSchedule?: (date: string, time: string) => void;
}

export const InterviewScheduler: React.FC<InterviewSchedulerProps> = ({ candidateId, onSchedule }) => {
  const [date, setDate] = React.useState('');
  const [time, setTime] = React.useState('');

  return (
    <div className="bg-surface-container rounded-lg border border-outline-variant p-6">
      <h3 className="font-semibold text-on-surface mb-4">Schedule Interview</h3>
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-on-surface-variant mb-2">Date</label>
          <input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            className="w-full px-4 py-2 bg-surface rounded-lg border border-outline-variant text-on-surface focus:outline-none focus:border-primary"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-on-surface-variant mb-2">Time</label>
          <input
            type="time"
            value={time}
            onChange={(e) => setTime(e.target.value)}
            className="w-full px-4 py-2 bg-surface rounded-lg border border-outline-variant text-on-surface focus:outline-none focus:border-primary"
          />
        </div>
        <div className="flex gap-2 justify-end pt-2">
          <Button variant="outline">Cancel</Button>
          <Button
            variant="primary"
            onClick={() => onSchedule?.(date, time)}
            disabled={!date || !time}
          >
            Schedule
          </Button>
        </div>
      </div>
    </div>
  );
};
