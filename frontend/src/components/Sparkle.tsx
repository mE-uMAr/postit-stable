import type { CSSProperties } from "react";

interface SparkleProps {
  size?: number;
  style?: CSSProperties;
}

export function Sparkle({ size = 16, style }: SparkleProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" style={style} aria-hidden="true">
      <path d="M12 2.5l2 6.2 6.2 2-6.2 2-2 6.2-2-6.2-6.2-2 6.2-2z" fill="currentColor" />
    </svg>
  );
}
