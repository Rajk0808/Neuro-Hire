import { cn, statusTone } from "@/lib/utils";

export function Badge({ label, tone }: { label: string; tone?: string }) {
  return <span className={cn("nh-badge", `nh-badge-${tone ?? statusTone(label)}`)}>{label.replaceAll("_", " ")}</span>;
}
