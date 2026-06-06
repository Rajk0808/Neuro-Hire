"use client";

import { motion } from "framer-motion";

export function ScoreBar({ value, color = "var(--teal)" }: { value: number; color?: string }) {
  return (
    <div className="score-track" aria-label={`Score ${value}`}>
      <motion.div
        className="score-fill"
        initial={{ width: 0 }}
        animate={{ width: `${Math.min(value, 100)}%` }}
        transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
        style={{ background: color }}
      />
    </div>
  );
}
