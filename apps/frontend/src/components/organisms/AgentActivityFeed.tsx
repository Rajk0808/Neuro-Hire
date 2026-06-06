import { Bot, Brain, CalendarCheck, Radar } from "lucide-react";
import { AgentStatusBadge } from "@/components/molecules/AgentStatusBadge";
import { ScoreBar } from "@/components/atoms/ScoreBar";
import { agentEvents } from "@/lib/mockData";

const icons = [Bot, Brain, CalendarCheck, Radar];

export function AgentActivityFeed() {
  return (
    <aside className="panel activity-feed">
      <div className="section-head">
        <div>
          <span>Live Control</span>
          <h2>Agent Activity</h2>
        </div>
        <div className="live-dot pulse-dot" />
      </div>
      {agentEvents.map((event, index) => {
        const Icon = icons[index % icons.length];
        return (
          <div className="activity-row" key={event.id}>
            <Icon />
            <div>
              <div className="activity-title">
                <strong>{event.agent}</strong>
                <AgentStatusBadge state={event.state} />
              </div>
              <p>{event.message}</p>
              <ScoreBar value={event.progress} />
              <small>{event.timestamp}</small>
            </div>
          </div>
        );
      })}
    </aside>
  );
}
