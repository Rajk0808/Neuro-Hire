'use client';

import React from 'react';

interface SheetProps {
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  children: React.ReactNode;
  side?: 'left' | 'right' | 'top' | 'bottom';
}

export const Sheet: React.FC<SheetProps> = ({
  open = false,
  onOpenChange,
  children,
  side = 'right',
}) => {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50">
      <div
        className="fixed inset-0 bg-black/50"
        onClick={() => onOpenChange?.(false)}
      />
      <div className={`fixed bg-surface-container border border-outline-variant h-full w-80 ${
        side === 'right' ? 'right-0' : 'left-0'
      }`}>
        {children}
      </div>
    </div>
  );
};
