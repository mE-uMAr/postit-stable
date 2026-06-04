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
      <style jsx>{`
        .pm {
          width: 100%;
          border: 1px solid var(--hairline);
          border-radius: var(--r-card);
          background: var(--surface);
          box-shadow: var(--e2);
          overflow: hidden;
        }
        .pm-bar {
          display: flex;
          gap: 7px;
          align-items: center;
          padding: 12px 14px;
          border-bottom: 1px solid var(--hairline);
          background: var(--surface-sunken);
        }
        .pm-dot {
          width: 10px;
          height: 10px;
          border-radius: 999px;
          background: var(--hairline);
        }
        .pm-body {
          padding: 18px;
          min-height: 220px;
          display: flex;
          flex-direction: column;
          gap: 12px;
        }
        .pm-line {
          height: 11px;
          border-radius: 6px;
          background: var(--surface-sunken);
        }
        .pm-chiprow {
          display: flex;
          gap: 8px;
          flex-wrap: wrap;
          margin-top: auto;
        }
        .pm-chip {
          width: 30px;
          height: 30px;
          border-radius: 9px;
          display: grid;
          place-items: center;
          color: #fff;
        }
        .pm-card {
          border: 1px solid var(--hairline);
          border-radius: 10px;
          padding: 12px;
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
        .pm-ai {
          align-self: flex-start;
          font: 600 11px var(--font-ui);
          color: var(--ai);
          background: var(--ai-tint);
          padding: 4px 10px;
          border-radius: 999px;
        }
        .pm-cal {
          display: grid;
          grid-template-columns: repeat(7, 1fr);
          gap: 6px;
        }
        .pm-cell {
          aspect-ratio: 1;
          border-radius: 7px;
          background: var(--surface-sunken);
        }
        .pm-cell.on {
          background: var(--spark-tint);
          border: 1px solid var(--spark);
        }
        .pm-cell.ai {
          background: var(--ai-tint);
          border: 1px dashed var(--ai);
        }
        .pm-row {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 9px 0;
          border-bottom: 1px solid var(--hairline);
        }
        .pm-status {
          margin-left: auto;
          width: 8px;
          height: 8px;
          border-radius: 999px;
          background: var(--success);
        }
      `}</style>
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
