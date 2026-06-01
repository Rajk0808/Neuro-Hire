'use client';

import React from 'react';
import { ScoreBar } from '@/components/atoms/ScoreBar';

interface ScoreGaugeProps {
  score: number;
  label?: string;
  size?: 'sm' | 'md' | 'lg';
}

export const ScoreGauge: React.FC<ScoreGaugeProps> = ({ score, label, size = 'md' }) => {
  const sizes = {
    sm: 'w-16 h-16 text-xs',
    md: 'w-24 h-24 text-sm',
    lg: 'w-32 h-32 text-base',
  };

  const getColor = (value: number) => {
    if (value >= 70) return 'text-green-500';
    if (value >= 40) return 'text-yellow-500';
    return 'text-red-500';
  };

  return (
    <div className="flex flex-col items-center gap-2">
      <div
        className={`flex items-center justify-center rounded-full border-4 border-surface-container-high ${sizes[size]}`}
      >
        <span className={`font-bold ${getColor(score)}`}>{Math.round(score)}%</span>
      </div>
      {label && <p className="text-xs text-on-surface-variant text-center">{label}</p>}
    </div>
  );
};
