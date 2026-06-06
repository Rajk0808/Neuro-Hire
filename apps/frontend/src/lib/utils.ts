import { clsx, type ClassValue } from "clsx";
import { formatDistanceToNow } from "date-fns";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatSalary(min: number, max: number, currency = "INR") {
  const symbol = currency === "INR" ? "Rs. " : "$";
  const compact = (value: number) => {
    if (currency === "INR" && value >= 10000000) return `${symbol}${(value / 10000000).toFixed(1)}Cr`;
    if (currency === "INR" && value >= 100000) return `${symbol}${(value / 100000).toFixed(0)}L`;
    if (value >= 1000) return `${symbol}${Math.round(value / 1000)}k`;
    return `${symbol}${value}`;
  };

  return `${compact(min)}-${compact(max)}`;
}

export function formatRelativeTime(dateString: string) {
  return formatDistanceToNow(new Date(dateString), { addSuffix: true });
}

export function statusTone(status: string) {
  if (["open", "active", "hired", "shortlisted"].includes(status)) return "good";
  if (["screening", "interviewing", "thinking", "interview_scheduled"].includes(status)) return "info";
  if (["warning", "rejected", "closed"].includes(status)) return "danger";
  return "neutral";
}
