'use client';

import React from 'react';
import { Candidate } from '@/types/candidate';
import { Avatar } from '@/components/atoms/Avatar';
import { Badge } from '@/components/atoms/Badge';
import { ScoreBar } from '@/components/atoms/ScoreBar';
import { formatRelativeTime } from '@/lib/utils';

interface CandidateCardProps {
  candidate: Candidate;
  onClick?: () => void;
}

export const CandidateCard: React.FC<CandidateCardProps> = ({ candidate, onClick }) => {
  return (
    <div
      onClick={onClick}
      className="p-4 bg-surface-container rounded-lg border border-outline-variant hover:border-primary/50 transition-all cursor-pointer"
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <Avatar src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${candidate.id}`} size="md" />
          <div>
            <h3 className="font-semibold text-on-surface">{candidate.name}</h3>
            <p className="text-sm text-on-surface-variant">{candidate.current_role}</p>
          </div>
        </div>
        {candidate.bias_flag && <Badge variant="warning">Bias Alert</Badge>}
      </div>

      <div className="space-y-2 mb-3">
        <p className="text-sm text-on-surface-variant">{candidate.current_company}</p>
        <div className="flex flex-wrap gap-1">
          {candidate.skills.slice(0, 3).map((skill) => (
            <Badge key={skill} variant="info">
              {skill}
            </Badge>
          ))}
          {candidate.skills.length > 3 && (
            <Badge variant="default">+{candidate.skills.length - 3}</Badge>
          )}
        </div>
      </div>

      <div className="mb-3">
        <ScoreBar score={candidate.retrieval_scores.rrf_score * 100} label="RRF Score" />
      </div>

      <div className="flex items-center justify-between text-xs text-on-surface-variant">
        <span>{formatRelativeTime(candidate.applied_at)}</span>
        <Badge variant="success">{candidate.status}</Badge>
      </div>
    </div>
  );
};
