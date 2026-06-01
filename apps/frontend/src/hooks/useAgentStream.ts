import { useEffect, useRef, useCallback } from 'react';
import { useAgentStore } from '@/store/agentStore';
import { WSMessage, AgentName } from '@/types/agent';

export function useAgentStream(agentName: AgentName, taskId?: string) {
  const ws = useRef<WebSocket | null>(null);
  const { updateAgentStatus, setActiveTask, setWSConnected } = useAgentStore();

  const connect = useCallback(() => {
    if (ws.current?.readyState === WebSocket.OPEN) return;

    try {
      const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL}/agent/${agentName}`;
      ws.current = new WebSocket(wsUrl);

      ws.current.onopen = () => {
        setWSConnected(true);
      };

      ws.current.onmessage = (event) => {
        try {
          const message: WSMessage = JSON.parse(event.data);

          updateAgentStatus(agentName, {
            status: message.type === 'AGENT_STARTED' ? 'running' : 
                    message.type === 'AGENT_COMPLETED' ? 'completed' :
                    message.type === 'TASK_FAILED' ? 'failed' : 'running',
            progress: message.progress || 0,
            current_step: message.message,
          });

          if (message.type === 'AGENT_COMPLETED' || message.type === 'TASK_FAILED') {
            setActiveTask(null);
          }
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        updateAgentStatus(agentName, { status: 'failed', error: 'Connection failed' });
      };

      ws.current.onclose = () => {
        setWSConnected(false);
      };
    } catch (error) {
      console.error('Failed to connect to WebSocket:', error);
    }
  }, [agentName, updateAgentStatus, setActiveTask, setWSConnected]);

  const disconnect = useCallback(() => {
    if (ws.current) {
      ws.current.close();
      ws.current = null;
    }
  }, []);

  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  return { ws: ws.current, connect, disconnect };
}
