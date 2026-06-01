'use client';

import React from 'react';
import { AgentState } from '@/types/agent';
import { Badge } from '@/components/atoms/Badge';

interface AgentStatusBadgeProps {
  agent: AgentState;
  compact?: boolean;
}

export const AgentStatusBadge: React.FC<AgentStatusBadgeProps> = ({ agent, compact = false }) => {
  const statusVariants = {
    idle: 'default',
    running: 'info',
    completed: 'success',
    failed: 'error',
    paused: 'warning',
  } as const;

  return (
    <div className={compact ? 'inline-block' : 'flex items-center gap-2'}>
      <Badge variant={statusVariants[agent.status]}>
        {agent.status.charAt(0).toUpperCase() + agent.status.slice(1)}
      </Badge>
      {!compact && agent.progress > 0 && agent.status === 'running' && (
        <span className="text-xs text-on-surface-variant">{agent.progress}%</span>
      )}
    </div>
  );
};
