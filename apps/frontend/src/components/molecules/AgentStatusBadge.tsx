import { Cpu } from "lucide-react";
import { Badge } from "@/components/atoms/Badge";
import type { AgentState } from "@/types/agent";

export function AgentStatusBadge({ state }: { state: AgentState }) {
  return (
    <span className="agent-pill">
      <Cpu size={14} />
      <span className="pulse-dot" />
      <Badge label={state} tone={state === "warning" ? "danger" : state === "idle" ? "neutral" : "info"} />
    </span>
  );
}
