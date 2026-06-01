import React from 'react';
import { cn } from '@/lib/utils';

interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'success' | 'warning' | 'error' | 'info';
}

export const Badge = React.forwardRef<HTMLDivElement, BadgeProps>(
  ({ className, variant = 'default', ...props }, ref) => {
    const variants = {
      default: 'bg-surface-container text-on-surface border border-outline',
      success: 'bg-green-500/10 text-green-500 border border-green-500/20',
      warning: 'bg-yellow-500/10 text-yellow-500 border border-yellow-500/20',
      error: 'bg-red-500/10 text-red-500 border border-red-500/20',
      info: 'bg-blue-500/10 text-blue-500 border border-blue-500/20',
    };

    return (
      <div
        ref={ref}
        className={cn(
          'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium',
          variants[variant],
          className
        )}
        {...props}
      />
    );
  }
);

Badge.displayName = 'Badge';
