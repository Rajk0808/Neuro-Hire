import { candidates } from "@/lib/mockData";

const columns = ["screened", "shortlisted", "interview_scheduled", "hired"];

export function PipelineKanban() {
  return (
    <div className="kanban">
      {columns.map((column) => (
        <section className="panel kanban-col" key={column}>
          <h3>{column.replaceAll("_", " ")}</h3>
          {candidates
            .filter((candidate) => candidate.status === column || (column === "screened" && candidate.status === "screened"))
            .map((candidate) => (
              <a className="kanban-card" href={`/dashboard/candidates/${candidate.id}`} key={candidate.id}>
                <strong>{candidate.name}</strong>
                <span>{candidate.current_role}</span>
              </a>
            ))}
          {column === "hired" ? <p className="empty-note">No hires in this sprint yet.</p> : null}
        </section>
      ))}
    </div>
  );
}
