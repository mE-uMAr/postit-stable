/* ============================================================
   Postit — motion helpers (framer-motion variants + utils)
   All variants degrade gracefully when the user prefers reduced motion.
   ============================================================ */

import type { Variants, Transition } from "framer-motion";

/** SSR-safe check for the user's reduced-motion preference. */
export function prefersReducedMotion(): boolean {
  return (
    typeof window !== "undefined" &&
    typeof window.matchMedia === "function" &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches
  );
}

export const easeOut: Transition["ease"] = [0.22, 1, 0.36, 1];

/** Fade + rise. Use as `variants={fadeUp}` with initial/animate or whileInView. */
export const fadeUp: Variants = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0, transition: { duration: 0.5, ease: easeOut } },
};

export const fadeIn: Variants = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { duration: 0.4, ease: easeOut } },
};

/** Parent that staggers its children's `show` state. */
export const staggerContainer = (stagger = 0.08, delay = 0): Variants => ({
  hidden: {},
  show: { transition: { staggerChildren: stagger, delayChildren: delay } },
});

/** Shorthand props for a reveal-on-scroll block. */
export const revealOnView = {
  initial: "hidden",
  whileInView: "show",
  viewport: { once: true, margin: "-80px" },
} as const;

/** Subtle press/hover for interactive cards & buttons. */
export const hoverLift = {
  whileHover: { y: -3 },
  whileTap: { scale: 0.985 },
  transition: { duration: 0.2, ease: easeOut },
} as const;
