import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { formatDistanceToNow } from 'date-fns';
import { JobStatus, Seniority } from '@/types/job';
import { CandidateStatus } from '@/types/candidate';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatSalary(min: number, max: number, currency: string = 'INR') {
  const formatter = new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: currency,
    maximumFractionDigits: 0,
  });
  
  const formatValue = (val: number) => {
    if (val >= 10000000) return `₹${(val / 10000000).toFixed(1)}Cr`;
    if (val >= 100000) return `₹${(val / 100000).toFixed(0)}L`;
    return formatter.format(val);
  };

  return `${formatValue(min)}–${formatValue(max)}`;
}

export function formatRelativeTime(dateString: string) {
  return formatDistanceToNow(new Date(dateString), { addSuffix: true });
}

export function getStatusColor(status: JobStatus | CandidateStatus | string) {
  switch (status) {
    case 'open':
    case 'applied':
    case 'hired':
      return 'text-green-500 bg-green-50 border-green-200';
    case 'screening':
    case 'interviewing':
    case 'shortlisted':
      return 'text-indigo-500 bg-indigo-50 border-indigo-200';
    case 'draft':
    case 'paused':
      return 'text-slate-500 bg-slate-50 border-slate-200';
    case 'failed':
    case 'rejected':
      return 'text-red-500 bg-red-50 border-red-200';
    default:
      return 'text-slate-500 bg-slate-50 border-slate-200';
  }
}

export function truncate(str: string, maxLen: number) {
  if (str.length <= maxLen) return str;
  return str.slice(0, maxLen) + '...';
}

export function getRRFColor(score: number) {
  if (score >= 0.7) return 'text-green-500';
  if (score >= 0.4) return 'text-yellow-500';
  return 'text-red-500';
}

export function getSeniorityLabel(seniority: Seniority): string {
  const labels: Record<Seniority, string> = {
    junior: 'Junior',
    mid: 'Mid-level',
    senior: 'Senior',
    staff: 'Staff',
    principal: 'Principal',
  };
  return labels[seniority];
}

export function getStatusLabel(status: string): string {
  return status
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}
