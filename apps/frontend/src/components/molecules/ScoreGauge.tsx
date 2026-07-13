"use client";

import { motion } from "framer-motion";

export function ScoreGauge({ value, label }: { value: number; label: string }) {
  const normalizedValue = Math.max(0, Math.min(value, 100));
  const roundedValue = Math.round(normalizedValue);
  const angle = (normalizedValue / 100) * 360;
  const tone = normalizedValue >= 80 ? "var(--green)" : normalizedValue >= 60 ? "var(--amber)" : "var(--rose)";
  return (
    <div className="score-gauge">
      <motion.div
        className="score-ring"
        initial={{ background: "conic-gradient(var(--primary) 0deg, var(--line) 0deg)" }}
        animate={{ background: `conic-gradient(${tone} ${angle}deg, var(--line) ${angle}deg)` }}
        transition={{ duration: 1 }}
      >
        <div>
          <strong>{roundedValue}</strong>
          <span>{label}</span>
        </div>
      </motion.div>
    </div>
  );
}
