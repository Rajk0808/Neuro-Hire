import { CalendarClock, Users } from "lucide-react";
import { candidates } from "@/lib/mockData";

export function InterviewScheduler() {
  return (
    <div className="panel scheduler">
      <div className="section-head">
        <div>
          <span>Orchestrator</span>
          <h2>Interview Scheduler</h2>
        </div>
        <CalendarClock />
      </div>
      {candidates.slice(0, 2).map((candidate, index) => (
        <div className="schedule-row" key={candidate.id}>
          <Users />
          <div>
            <strong>{candidate.name}</strong>
            <span>{index === 0 ? "Technical panel · Monday 11:00" : "Hiring manager · Tuesday 15:30"}</span>
          </div>
        </div>
      ))}
    </div>
  );
}
