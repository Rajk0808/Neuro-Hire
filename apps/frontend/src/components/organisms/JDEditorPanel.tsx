'use client';

import React from 'react';
import { Button } from '@/components/atoms/Button';

interface JDEditorPanelProps {
  jobId?: string;
  onSave?: (content: string) => void;
}

export const JDEditorPanel: React.FC<JDEditorPanelProps> = ({ jobId, onSave }) => {
  const [content, setContent] = React.useState('');

  return (
    <div className="bg-surface-container rounded-lg border border-outline-variant p-6">
      <h3 className="font-semibold text-on-surface mb-4">Job Description Editor</h3>
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder="Paste your job description or voice note transcript here..."
        className="w-full h-64 p-4 bg-surface rounded-lg border border-outline-variant text-on-surface placeholder:text-on-surface-variant focus:outline-none focus:border-primary resize-none"
      />
      <div className="mt-4 flex gap-2 justify-end">
        <Button variant="outline">Cancel</Button>
        <Button variant="primary" onClick={() => onSave?.(content)}>
          Save & Generate
        </Button>
      </div>
    </div>
  );
};
