"use client";

import { PlatformLogo } from "@/components/PlatformLogo";
import type { PlatformKey } from "@/lib/types";

type Variant = "compose" | "ai" | "calendar" | "connections";

const CHIPS: PlatformKey[] = ["x", "linkedin", "instagram", "threads", "facebook"];

/** Lightweight, on-brand product visual used in place of screenshots. */
export function ProductMock({ variant = "compose" }: { variant?: Variant }) {
  return (
    <div className="pm">
      <div className="pm-bar">
        <span className="pm-dot" />
        <span className="pm-dot" />
        <span className="pm-dot" />
      </div>
      <div className="pm-body">{renderBody(variant)}</div>
    </div>
  );
}

function renderBody(variant: Variant) {
  if (variant === "ai") {
    return (
      <>
        <span className="pm-ai">✨ AI rewriting for each platform…</span>
        <div className="pm-card">
          <div className="pm-line" style={{ width: "90%" }} />
          <div className="pm-line" style={{ width: "70%" }} />
        </div>
        <div className="pm-card">
          <div className="pm-line" style={{ width: "80%" }} />
          <div className="pm-line" style={{ width: "55%" }} />
        </div>
        <div className="pm-chiprow">
          {CHIPS.map((k) => (
            <span key={k} className="pm-chip" style={{ background: `var(--pf-${k})` }}>
              <PlatformLogo platform={k} />
            </span>
          ))}
        </div>
      </>
    );
  }

  if (variant === "calendar") {
    const on = new Set([3, 5, 9, 12, 16]);
    const ai = new Set([11, 19]);
    return (
      <div className="pm-cal">
        {Array.from({ length: 28 }).map((_, i) => (
          <div key={i} className={"pm-cell" + (on.has(i) ? " on" : ai.has(i) ? " ai" : "")} />
        ))}
      </div>
    );
  }

  if (variant === "connections") {
    return (
      <>
        {CHIPS.map((k) => (
          <div key={k} className="pm-row">
            <span className="pm-chip" style={{ background: `var(--pf-${k})`, width: 26, height: 26 }}>
              <PlatformLogo platform={k} />
            </span>
            <div className="pm-line" style={{ width: 120 }} />
            <span className="pm-status" />
          </div>
        ))}
      </>
    );
  }

  // compose (default)
  return (
    <>
      <div className="pm-card">
        <div className="pm-line" style={{ width: "95%" }} />
        <div className="pm-line" style={{ width: "85%" }} />
        <div className="pm-line" style={{ width: "60%" }} />
      </div>
      <div className="pm-chiprow">
        {CHIPS.map((k) => (
          <span key={k} className="pm-chip" style={{ background: `var(--pf-${k})` }}>
            <PlatformLogo platform={k} />
          </span>
        ))}
      </div>
    </>
  );
}
