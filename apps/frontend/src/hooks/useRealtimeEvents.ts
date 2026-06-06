"use client";

import { useAgentStream } from "@/hooks/useAgentStream";

export function useRealtimeEvents() {
  return {
    connected: true,
    events: useAgentStream()
  };
}
