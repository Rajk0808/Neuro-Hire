"use client";

import { motion } from "framer-motion";

export function ScoreGauge({ value, label }: { value: number; label: string }) {
  const angle = (Math.min(value, 100) / 100) * 360;
  return (
    <div className="score-gauge">
      <motion.div
        className="score-ring"
        initial={{ background: "conic-gradient(var(--primary) 0deg, var(--line) 0deg)" }}
        animate={{ background: `conic-gradient(var(--teal) ${angle}deg, var(--line) ${angle}deg)` }}
        transition={{ duration: 1 }}
      >
        <div>
          <strong>{value}</strong>
          <span>{label}</span>
        </div>
      </motion.div>
    </div>
  );
}
