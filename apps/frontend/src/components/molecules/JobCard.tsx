"use client";

import { ArrowRight, BriefcaseBusiness, MapPin, ShieldCheck } from "lucide-react";
import { motion } from "framer-motion";
import { Badge } from "@/components/atoms/Badge";
import { ScoreBar } from "@/components/atoms/ScoreBar";
import { formatSalary } from "@/lib/utils";
import type { Job } from "@/types/job";

export function JobCard({ job }: { job: Job }) {
  return (
    <motion.article className="panel job-card scanline" whileHover={{ y: -4, borderColor: "rgba(142, 161, 255, 0.7)" }}>
      <div className="job-card-head">
        <BriefcaseBusiness />
        <Badge label={job.status} />
      </div>
      <h3>{job.title}</h3>
      <p><MapPin size={14} /> {job.department} · {job.location}</p>
      <div className="chip-row">
        {job.required_skills.slice(0, 4).map((skill) => <span key={skill}>{skill}</span>)}
      </div>
      <div className="job-card-metrics">
        <span>{formatSalary(job.salary_min, job.salary_max, job.currency)}</span>
        <span>{job.shortlist_count} shortlisted</span>
      </div>
      <div className="dei-line">
        <ShieldCheck size={16} />
        <ScoreBar value={job.dei_score} color="var(--amber)" />
        <strong>{job.dei_score}</strong>
      </div>
      <a href={`/dashboard/jobs/${job.id}`} className="card-link">
        Open requisition <ArrowRight size={16} />
      </a>
    </motion.article>
  );
}
