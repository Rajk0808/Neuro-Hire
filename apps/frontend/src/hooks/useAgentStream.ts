"use client";

import { useEffect, useState } from "react";
import { agentEvents } from "@/lib/mockData";

export function useAgentStream() {
  const [events, setEvents] = useState(agentEvents);

  useEffect(() => {
    const timer = setInterval(() => {
      setEvents((current) => current.map((event) => ({ ...event, progress: Math.min(100, event.progress + 1) })));
    }, 1800);
    return () => clearInterval(timer);
  }, []);

  return events;
}
