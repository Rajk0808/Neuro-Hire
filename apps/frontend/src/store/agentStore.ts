import { create } from 'zustand';
import { AgentState, TaskStatus } from '@/types/agent';

interface AgentStore {
  agents: Record<string, AgentState>;
  activeTask: TaskStatus | null;
  wsConnected: boolean;
  updateAgentStatus: (agentName: string, status: Partial<AgentState>) => void;
  setActiveTask: (task: TaskStatus | null) => void;
  setWSConnected: (connected: boolean) => void;
  getAgentStatus: (agentName: string) => AgentState | undefined;
  reset: () => void;
}

export const useAgentStore = create<AgentStore>((set, get) => ({
  agents: {},
  activeTask: null,
  wsConnected: false,
  updateAgentStatus: (agentName, status) =>
    set((state) => ({
      agents: {
        ...state.agents,
        [agentName]: { ...state.agents[agentName], ...status },
      },
    })),
  setActiveTask: (task) => set({ activeTask: task }),
  setWSConnected: (connected) => set({ wsConnected: connected }),
  getAgentStatus: (agentName) => get().agents[agentName],
  reset: () => set({ agents: {}, activeTask: null, wsConnected: false }),
}));
