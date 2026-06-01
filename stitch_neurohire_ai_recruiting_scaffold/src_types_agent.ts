export type AgentName =
  | 'jd-architect' | 'resume-intelligence' | 'interview-orchestrator'
  | 'candidate-companion' | 'evaluation-synthesis' | 'bias-guardian'
  | 'market-intelligence' | 'self-healing-ops'

export type AgentStatus = 'idle' | 'running' | 'completed' | 'failed' | 'paused'

export interface AgentState {
  name: AgentName
  status: AgentStatus
  current_step?: string
  progress: number          // 0–100
  last_run?: string
  task_id?: string
  error?: string
}

export type WSMessageType =
  | 'AGENT_STARTED' | 'AGENT_STEP' | 'AGENT_COMPLETED'
  | 'BIAS_ALERT' | 'TASK_FAILED'

export interface WSMessage {
  type: WSMessageType
  agent: AgentName
  task_id: string
  step?: number
  message?: string
  progress?: number
  result_url?: string
  severity?: 'low' | 'medium' | 'high'
}

export interface TaskStatus {
  task_id: string
  status: 'queued' | 'running' | 'completed' | 'failed'
  progress: number
  current_step: string
  result?: Record<string, unknown>
  error?: string
}
