import React from 'react';
import { cn } from '@/lib/utils';

interface AvatarProps extends React.ImgHTMLAttributes<HTMLImageElement> {
  size?: 'sm' | 'md' | 'lg';
  status?: 'online' | 'offline' | 'idle';
}

export const Avatar = React.forwardRef<HTMLImageElement, AvatarProps>(
  ({ className, size = 'md', status, ...props }, ref) => {
    const sizes = {
      sm: 'w-6 h-6',
      md: 'w-10 h-10',
      lg: 'w-16 h-16',
    };

    const statusStyles = {
      online: 'bg-green-500',
      offline: 'bg-gray-500',
      idle: 'bg-yellow-500',
    };

    return (
      <div className="relative inline-block">
        <img
          ref={ref}
          className={cn('rounded-full object-cover border-2 border-surface-container', sizes[size], className)}
          {...props}
        />
        {status && (
          <div
            className={cn(
              'absolute bottom-0 right-0 w-2 h-2 rounded-full border border-surface-container',
              statusStyles[status]
            )}
          />
        )}
      </div>
    );
  }
);

Avatar.displayName = 'Avatar';
