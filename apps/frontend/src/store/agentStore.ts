import { create } from "zustand";
import { agentEvents } from "@/lib/mockData";
import type { AgentEvent } from "@/types/agent";

type AgentStore = {
  events: AgentEvent[];
};

export const useAgentStore = create<AgentStore>(() => ({ events: agentEvents }));
