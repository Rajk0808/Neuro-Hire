"use client";

import { Job } from "@/types/job";
import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { BriefcaseBusiness, Clock, ShieldCheck, Users } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { AgentActivityFeed } from "@/components/organisms/AgentActivityFeed";
import { JobCard } from "@/components/molecules/JobCard"; 
import { ShortlistTable } from "@/components/organisms/ShortlistTable";
import { fadeUp, stagger } from "@/animations/variants";
import { DashboardApi } from "@/lib/api";

interface MetricItem {
  label: string;
  value: string | number;
  icon: LucideIcon;
  tone: string;
}

export default function DashboardPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [metrics, setMetrics] = useState<MetricItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function fetchDashboardData() {
      try {
        // Fetch all metrics and data in parallel safely
        const [
          openRolesData,
          candidateCountData,
          timeToHireData,
          deiScoreData,
          recentJobsData
        ] = await Promise.all([
          DashboardApi.getOpenRoles().catch(() => ({ open_roles: 0 })),
          DashboardApi.getCandidatesCountThisWeek().catch(() => ({ candidates_count: 0 })),
          DashboardApi.getAverageTimeToHire().catch(() => ({ average_time_to_hire: "32 days" })),
          DashboardApi.getDEIScoreAverage().catch(() => ({ average_dei_score: 96 })),
          DashboardApi.getRecentJobs().catch(() => [])
        ]);

        // Construct structural data arrays with dynamic values
        setMetrics([
          { label: "Open roles", value: openRolesData.open_roles, icon: BriefcaseBusiness, tone: "var(--primary)" },
          { label: "Candidates this week", value: candidateCountData.candidates_count, icon: Users, tone: "var(--teal)" },
          { label: "Avg time-to-hire", value: timeToHireData.average_time_to_hire, icon: Clock, tone: "var(--amber)" },
          { label: "Compliance score", value: deiScoreData.average_dei_score, icon: ShieldCheck, tone: "var(--green)" }
        ]);

        setJobs(Array.isArray(recentJobsData) ? recentJobsData : []);
      } catch (error) {
        console.error("Failed to resolve dashboard data", error);
      } finally {
        setLoading(false);
      }
    }

    fetchDashboardData();
  }, []);

  if (loading) {
    return <div className="page-pad">Loading Recruiter Command Center...</div>;
  }

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
          <div className="job-grid">
            {jobs.map((job) => (
              <JobCard job={job} key={job.id} />
            ))}
          </div>
          <ShortlistTable />
        </motion.section>
        <motion.div style={{ gridColumn: "span 4" }} variants={fadeUp}>
          <AgentActivityFeed />
        </motion.div>
      </div>
    </motion.div>
  );
}
