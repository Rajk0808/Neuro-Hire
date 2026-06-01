import { useEffect, useState } from 'react';
import { useMotionValue, useTransform } from 'framer-motion';

interface AnimatedScoreOptions {
  from?: number;
  to: number;
  duration?: number;
}

export function useAnimatedScore({ from = 0, to, duration = 1 }: AnimatedScoreOptions) {
  const count = useMotionValue(from);
  const rounded = useTransform(count, (latest) => Math.round(latest));

  useEffect(() => {
    const animation = requestAnimationFrame(() => {
      let current = from;
      const increment = (to - from) / (duration * 60);
      
      const interval = setInterval(() => {
        current += increment;
        if (current >= to) {
          count.set(to);
          clearInterval(interval);
        } else {
          count.set(current);
        }
      }, 1000 / 60);

      return () => clearInterval(interval);
    });

    return () => cancelAnimationFrame(animation);
  }, [count, from, to, duration]);

  return rounded;
}
