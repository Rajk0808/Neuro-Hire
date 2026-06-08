"use client";

import type { ReactNode } from "react";
import { motion, type HTMLMotionProps } from "framer-motion";
import { cn } from "@/lib/utils";

// 1. Omit both variant and children to secure absolute control over UI typing
type ButtonProps = Omit<HTMLMotionProps<"button">, "variant" | "children"> & {
  variant?: "primary" | "ghost" | "danger";
  icon?: ReactNode;
  children?: ReactNode;
};

export function Button({
  className,
  variant = "primary",
  icon,
  children,
  ...props // 2. props is now clean and holds no complex child union states
}: ButtonProps) {
  return (
    <motion.button
      whileHover={{ y: -1 }}
      whileTap={{ scale: 0.98 }}
      className={cn("nh-button", `nh-button-${variant}`, className)}
      {...props}
    >
      {icon && <span className="nh-button-icon">{icon}</span>}
      {children}
    </motion.button>
  );
}
