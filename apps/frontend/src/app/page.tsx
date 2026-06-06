"use client";

import { motion } from "framer-motion";
import { ArrowRight, Brain, CircuitBoard, ShieldCheck, Sparkles } from "lucide-react";
import { Button } from "@/components/atoms/Button";
import { AgentActivityFeed } from "@/components/organisms/AgentActivityFeed";
import { fadeUp, stagger } from "@/animations/variants";

export default function LandingPage() {
  return (
    <main className="landing-page">
      <nav className="landing-nav">
        <a className="brand" href="/">
          <span>NH</span>
          <strong>NeuroHire</strong>
        </a>
        <div>
          <a href="/login">Login</a>
          <a href="/dashboard">Dashboard</a>
        </div>
      </nav>
      <motion.section className="hero" variants={stagger} initial="hidden" animate="show">
        <motion.div className="hero-copy" variants={fadeUp}>
          <span className="eyebrow"><Sparkles size={16} /> Multi-agent recruiting intelligence</span>
          <h1>NeuroHire</h1>
          <p>Autonomous sourcing, bias-aware screening, JD design, interview orchestration, and market intelligence in one animated command center.</p>
          <div className="hero-actions">
            <a href="/dashboard"><Button icon={<ArrowRight size={16} />}>Launch command center</Button></a>
            <a href="/candidate"><Button variant="ghost">Candidate portal</Button></a>
          </div>
        </motion.div>
        <motion.div className="hero-console panel scanline" variants={fadeUp}>
          <div className="console-strip"><span /> <span /> <span /></div>
          <div className="signal-map">
            <div><Brain /> JD Architect</div>
            <div><CircuitBoard /> Resume Intelligence</div>
            <div><ShieldCheck /> Bias Guardian</div>
          </div>
          <AgentActivityFeed />
        </motion.div>
      </motion.section>
    </main>
  );
}
