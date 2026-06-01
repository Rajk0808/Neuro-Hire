'use client';

import React from 'react';
import { Candidate } from '@/types/candidate';
import { formatRelativeTime, getStatusColor } from '@/lib/utils';

interface ShortlistTableProps {
  candidates: Candidate[];
  onRowClick?: (candidate: Candidate) => void;
  loading?: boolean;
}

export const ShortlistTable: React.FC<ShortlistTableProps> = ({
  candidates,
  onRowClick,
  loading,
}) => {
  return (
    <div className="bg-surface-container rounded-lg border border-outline-variant overflow-hidden">
      <table className="w-full">
        <thead className="bg-surface-container-high">
          <tr>
            <th className="px-6 py-3 text-left text-sm font-semibold text-on-surface">Name</th>
            <th className="px-6 py-3 text-left text-sm font-semibold text-on-surface">Role</th>
            <th className="px-6 py-3 text-left text-sm font-semibold text-on-surface">Status</th>
            <th className="px-6 py-3 text-left text-sm font-semibold text-on-surface">RRF Score</th>
            <th className="px-6 py-3 text-left text-sm font-semibold text-on-surface">Applied</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-outline-variant">
          {candidates.map((candidate) => (
            <tr
              key={candidate.id}
              onClick={() => onRowClick?.(candidate)}
              className="hover:bg-surface-container-high transition-colors cursor-pointer"
            >
              <td className="px-6 py-4 text-sm text-on-surface">{candidate.name}</td>
              <td className="px-6 py-4 text-sm text-on-surface-variant">{candidate.current_role}</td>
              <td className="px-6 py-4 text-sm">
                <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(candidate.status)}`}>
                  {candidate.status}
                </span>
              </td>
              <td className="px-6 py-4 text-sm text-on-surface font-medium">
                {(candidate.retrieval_scores.rrf_score * 100).toFixed(0)}%
              </td>
              <td className="px-6 py-4 text-sm text-on-surface-variant">
                {formatRelativeTime(candidate.applied_at)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {loading && <div className="p-8 text-center text-on-surface-variant">Loading...</div>}
      {!loading && candidates.length === 0 && (
        <div className="p-8 text-center text-on-surface-variant">No candidates found</div>
      )}
    </div>
  );
};
