'use client';

import React from 'react';
import { AgentState } from '@/types/agent';
import { AgentStatusBadge } from '@/components/molecules/AgentStatusBadge';

interface AgentActivityFeedProps {
  agents: AgentState[];
}

export const AgentActivityFeed: React.FC<AgentActivityFeedProps> = ({ agents }) => {
  return (
    <div className="bg-surface-container rounded-lg border border-outline-variant p-6">
      <h3 className="font-semibold text-on-surface mb-4">Agent Activity</h3>
      <div className="space-y-4">
        {agents.map((agent) => (
          <div key={agent.name} className="flex items-center justify-between py-3 border-b border-outline-variant last:border-b-0">
            <div className="flex-1">
              <h4 className="font-medium text-on-surface capitalize">{agent.name.replace(/-/g, ' ')}</h4>
              {agent.current_step && (
                <p className="text-xs text-on-surface-variant mt-1">{agent.current_step}</p>
              )}
            </div>
            <div className="flex items-center gap-4">
              {agent.status === 'running' && (
                <span className="text-xs text-on-surface-variant">{agent.progress}%</span>
              )}
              <AgentStatusBadge agent={agent} compact />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
