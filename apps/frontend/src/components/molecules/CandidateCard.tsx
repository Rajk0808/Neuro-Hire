"use client";

import { ArrowRight, MapPin, Sparkles } from "lucide-react";
import { motion } from "framer-motion";
import { Avatar } from "@/components/atoms/Avatar";
import { Badge } from "@/components/atoms/Badge";
import { ScoreBar } from "@/components/atoms/ScoreBar";
import type { Candidate } from "@/types/candidate";
import Link from "next/link";
import type { Route } from "next";

export function CandidateCard({ candidate }: { candidate: Candidate }) {
  const score = Math.round(candidate.retrieval_scores.rrf_score * 100);
  return (
    <motion.article className="panel candidate-card" whileHover={{ y: -3 }}>
      <div className="candidate-top">
        <Avatar name={candidate.name} />
        <div>
          <h3>{candidate.name}</h3>
          <p>{candidate.current_role}</p>
        </div>
        <Badge label={candidate.status} />
      </div>
      <p className="candidate-location"><MapPin size={14} /> {candidate.location} · {candidate.experience_years} yrs</p>
      <div className="chip-row">
        {candidate.skills.slice(0, 4).map((skill) => <span key={skill}>{skill}</span>)}
      </div>
      <div className="match-row">
        <Sparkles size={16} />
        <ScoreBar value={score} />
        <strong>{score}%</strong>
      </div>
      <Link href={`/dashboard/candidates/${candidate.id}` as Route} className="card-link">
        View intelligence <ArrowRight size={16} />
      </Link>
    </motion.article>
  );
}
