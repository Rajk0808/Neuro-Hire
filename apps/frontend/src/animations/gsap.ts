// GSAP Timeline configurations
export const pageTransitionTimeline = {
  duration: 0.6,
  ease: 'power2.inOut',
};

export const elementStagger = {
  amount: 0.1,
  from: 'start',
};

export const containerConfig = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2,
    },
  },
};
