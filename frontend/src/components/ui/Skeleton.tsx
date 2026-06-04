"use client";

import type { CSSProperties } from "react";

interface SkeletonProps {
  width?: number | string;
  height?: number | string;
  radius?: number | string;
  style?: CSSProperties;
  className?: string;
}

/** A single shimmering placeholder block. */
export function Skeleton({ width, height = 16, radius = 8, style, className }: SkeletonProps) {
  return (
    <span
      className={"sk" + (className ? " " + className : "")}
      style={{ width: width ?? "100%", height, borderRadius: radius, ...style }}
      aria-hidden
    />
  );
}

/** A stack of text lines. */
export function SkeletonText({ lines = 3, gap = 10 }: { lines?: number; gap?: number }) {
  return (
    <span style={{ display: "flex", flexDirection: "column", gap }}>
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton key={i} width={i === lines - 1 ? "60%" : "100%"} height={12} />
      ))}
    </span>
  );
}

/** Repeated card skeletons for grids/lists. */
export function SkeletonCards({ count = 3, height = 120 }: { count?: number; height?: number }) {
  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <Skeleton key={i} height={height} radius={14} />
      ))}
    </>
  );
}
