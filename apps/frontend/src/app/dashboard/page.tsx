"use client";

import { motion } from "framer-motion";
import { BriefcaseBusiness, Clock, ShieldCheck, Users } from "lucide-react";
import { AgentActivityFeed } from "@/components/organisms/AgentActivityFeed";
import { JobCard } from "@/components/molecules/JobCard";
import { ShortlistTable } from "@/components/organisms/ShortlistTable";
import { jobs } from "@/lib/mockData";
import { fadeUp, stagger } from "@/animations/variants";

const metrics = [
  { label: "Open roles", value: "42", icon: BriefcaseBusiness, tone: "var(--primary)" },
  { label: "Candidates this week", value: "1,284", icon: Users, tone: "var(--teal)" },
  { label: "Avg time-to-hire", value: "14.5d", icon: Clock, tone: "var(--amber)" },
  { label: "Compliance score", value: "98.2", icon: ShieldCheck, tone: "var(--green)" }
];

export default function DashboardPage() {
  return (
    <motion.div className="page-pad" variants={stagger} initial="hidden" animate="show">
      <motion.div className="metric-row" variants={stagger}>
        {metrics.map((metric) => {
          const Icon = metric.icon;
          return (
            <motion.section className="panel metric-card" variants={fadeUp} key={metric.label}>
              <Icon style={{ color: metric.tone }} />
              <span>{metric.label}</span>
              <strong>{metric.value}</strong>
            </motion.section>
          );
        })}
      </motion.div>
      <div className="dashboard-grid main-grid">
        <motion.section style={{ gridColumn: "span 8" }} variants={fadeUp}>
          <div className="section-head">
            <div>
              <span>Command Center</span>
              <h1>Recruiter Dashboard</h1>
            </div>
          </div>
          <div className="job-grid">{jobs.map((job) => <JobCard job={job} key={job.id} />)}</div>
          <ShortlistTable />
        </motion.section>
        <motion.div style={{ gridColumn: "span 4" }} variants={fadeUp}>
          <AgentActivityFeed />
        </motion.div>
      </div>
    </motion.div>
  );
}
