// Spring physics configurations for Framer Motion
export const springConfig = {
  default: { type: 'spring', stiffness: 100, damping: 10 },
  bouncy: { type: 'spring', stiffness: 150, damping: 8 },
  smooth: { type: 'spring', stiffness: 80, damping: 20 },
  tight: { type: 'spring', stiffness: 200, damping: 25 },
};

export const transitionConfig = {
  fast: { duration: 0.2 },
  normal: { duration: 0.35 },
  slow: { duration: 0.6 },
};
