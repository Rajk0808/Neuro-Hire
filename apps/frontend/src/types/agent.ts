export type AgentState = "active" | "thinking" | "idle" | "warning";

export interface AgentEvent {
  id: string;
  agent: string;
  state: AgentState;
  message: string;
  progress: number;
  timestamp: string;
}
