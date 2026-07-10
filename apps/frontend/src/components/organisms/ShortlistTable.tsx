"use client"; 

import { useState, useEffect } from "react";
import { Badge } from "@/components/atoms/Badge";
import { ScoreBar } from "@/components/atoms/ScoreBar";
import { DashboardApi } from "@/lib/api";
import Link from "next/link";
import type { Route } from "next";

interface Candidate {
  id: string | number;
  name: string;
  current_role: string;
  location: string;
  status: string;
  rrf_score: number;
}

const toCandidateRow = (input: unknown): Candidate | null => {
  if (!input || typeof input !== "object") {
    return null;
  }

  const row = input as Record<string, unknown>;
  const retrievalScores =
    row.retrieval_scores && typeof row.retrieval_scores === "object"
      ? (row.retrieval_scores as Record<string, unknown>)
      : undefined;

  const id = row.id;
  if (typeof id !== "string" && typeof id !== "number") {
    return null;
  }

  const rrfFromNested = retrievalScores?.rrf_score;
  const rrfScore =
    typeof row.rrf_score === "number"
      ? row.rrf_score
      : typeof rrfFromNested === "number"
        ? rrfFromNested
        : 0;

  return {
    id,
    name: typeof row.name === "string" ? row.name : "Unknown Candidate",
    current_role: typeof row.current_role === "string" ? row.current_role : "Unspecified role",
    location: typeof row.location === "string" ? row.location : "Unknown",
    status: typeof row.status === "string" ? row.status : "screened",
    rrf_score: rrfScore
  };
};

export function ShortlistTable() {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    DashboardApi.getRecentRecruiterActivities()
      .then((data) => {
        const normalizedCandidates = Array.isArray(data)
          ? data.map(toCandidateRow).filter((candidate): candidate is Candidate => candidate !== null)
          : [];
        setCandidates(normalizedCandidates);
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
          <Link href={`/dashboard/candidates/${candidate.id}` as Route} className="nh-row" key={candidate.id}>
            <strong>{candidate.name}</strong>
            <span>{candidate.current_role}</span>
            <span>{candidate.location}</span>
            <Badge label={candidate.status} />
            <ScoreBar value={Math.round((candidate.rrf_score || 0) * 100)} />
          </Link>
        ))}
      </div>
    </div>
  );
}
