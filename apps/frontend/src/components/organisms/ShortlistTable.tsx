"use client"; 

import { useState, useEffect } from "react";
import { Badge } from "@/components/atoms/Badge";
import { ScoreBar } from "@/components/atoms/ScoreBar";
import { DashboardApi } from "@/lib/api";

interface Candidate {
  id: string | number;
  name: string;
  current_role: string;
  location: string;
  status: string;
  rrf_score: number;
  
}

export function ShortlistTable() {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    DashboardApi.getRecentRecruiterActivities()
      .then((data) => {
        setCandidates(Array.isArray(data) ? data : []);
      })
      .catch((error) => {
        console.error("Failed to fetch candidates:", error);
        setCandidates([]);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="panel table-panel">Loading candidates...</div>;
  }

  return (
    <div className="panel table-panel">
      <div className="section-head">
        <div>
          <span>Shortlist</span>
          <h2>Ranked Candidates</h2>
        </div>
      </div>
      <div className="nh-table">
        {candidates?.map((candidate) => (
          <a href={`/dashboard/candidates/${candidate.id}`} className="nh-row" key={candidate.id}>
            <strong>{candidate.name}</strong>
            <span>{candidate.current_role}</span>
            <span>{candidate.location}</span>
            <Badge label={candidate.status} />
            <ScoreBar value={Math.round((candidate.rrf_score || 0) * 100)} />
          </a>
        ))}
      </div>
    </div>
  );
}
