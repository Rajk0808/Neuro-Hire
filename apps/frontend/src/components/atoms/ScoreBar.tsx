import React from 'react';
import { cn } from '@/lib/utils';

interface ScoreBarProps extends React.HTMLAttributes<HTMLDivElement> {
  score: number; // 0–100
  label?: string;
  showValue?: boolean;
}

export const ScoreBar = React.forwardRef<HTMLDivElement, ScoreBarProps>(
  ({ className, score, label, showValue = true, ...props }, ref) => {
    const getColor = (value: number) => {
      if (value >= 70) return 'bg-green-500';
      if (value >= 40) return 'bg-yellow-500';
      return 'bg-red-500';
    };

    return (
      <div ref={ref} className={cn('space-y-1', className)} {...props}>
        {label && <p className="text-sm font-medium text-on-surface-variant">{label}</p>}
        <div className="w-full h-2 bg-surface-container-high rounded-full overflow-hidden">
          <div
            className={cn('h-full transition-all duration-300', getColor(score))}
            style={{ width: `${Math.min(score, 100)}%` }}
          />
        </div>
        {showValue && <p className="text-xs text-on-surface-variant">{Math.round(score)}%</p>}
      </div>
    );
  }
);

ScoreBar.displayName = 'ScoreBar';
