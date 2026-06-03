"use client";

import { useState } from "react";
import { Icon } from "@/components/Icon";
import { Sparkle } from "@/components/Sparkle";
import { PF } from "@/lib/platforms";
import type { PlatformKey } from "@/lib/types";

const DOW = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

interface CalPost {
  t: string;
  tm: string;
  pfs: PlatformKey[];
}

// Scheduled posts keyed by day-of-month (June 2026)
const CAL_POSTS: Record<number, CalPost[]> = {
  3: [{ t: "Spring collection launch", tm: "9:00", pfs: ["x", "linkedin", "instagram"] }],
  5: [{ t: "Behind the scenes", tm: "12:30", pfs: ["instagram", "threads"] }],
  9: [{ t: "Customer spotlight", tm: "8:00", pfs: ["linkedin", "facebook"] }],
  12: [
    { t: "Weekend sale teaser", tm: "17:00", pfs: ["x", "threads", "facebook"] },
    { t: "New blog post", tm: "10:00", pfs: ["wordpress"] },
  ],
  16: [{ t: "Product tip #4", tm: "9:00", pfs: ["x", "linkedin"] }],
  18: [{ t: "Founder Q&A short", tm: "15:00", pfs: ["youtube", "tiktok"] }],
  23: [{ t: "Restock announcement", tm: "9:00", pfs: ["x", "instagram", "facebook"] }],
};
const GHOST: Record<number, string> = { 11: "14:00", 19: "9:00", 25: "11:30" }; // AI best-time suggestions

interface Cell {
  d: number;
  dim: boolean;
}

function buildMonth(year: number, month: number): Cell[] {
  const first = new Date(year, month, 1).getDay();
  const days = new Date(year, month + 1, 0).getDate();
  const prevDays = new Date(year, month, 0).getDate();
  const cells: Cell[] = [];
  for (let i = 0; i < first; i++) cells.push({ d: prevDays - first + i + 1, dim: true });
  for (let d = 1; d <= days; d++) cells.push({ d, dim: false });
  while (cells.length % 7 !== 0) cells.push({ d: cells.length - first - days + 1, dim: true });
  return cells;
}

export function Calendar() {
  const [view, setView] = useState("Month");
  const cells = buildMonth(2026, 5); // June 2026
  const today = 3;

  return (
    <div className="view-pad">
      <div className="vh">
        <div className="vh-title">
          <h2>Calendar</h2>
          <p>Drag posts to reschedule. Ghost slots are AI best-time suggestions.</p>
        </div>
        <div className="vh-actions">
          <div className="seg">
            {["Month", "Week", "Queue"].map((v) => (
              <button key={v} className={view === v ? "on" : ""} onClick={() => setView(v)}>
                {v}
              </button>
            ))}
          </div>
          <button className="btn btn-secondary">
            <Icon name="plus" size={17} /> Add to queue
          </button>
        </div>
      </div>

      <div className="cal-wrap">
        <div className="cal-head">
          <div className="mo">June 2026</div>
          <div className="cal-nav">
            <button>
              <Icon name="chevl" size={17} />
            </button>
            <button>
              <Icon name="chevr" size={17} />
            </button>
          </div>
          <span className="spacer" />
          <span className="pill">
            <span className="badge-dot" style={{ background: "var(--ai)" }} /> AI best-time
          </span>
        </div>
        <div className="cal-grid">
          {DOW.map((d) => (
            <div key={d} className="cal-dow">
              {d}
            </div>
          ))}
          {cells.map((c, i) => {
            const posts = !c.dim ? CAL_POSTS[c.d] : undefined;
            const ghost = !c.dim ? GHOST[c.d] : undefined;
            return (
              <div
                key={i}
                className={"cal-cell" + (c.dim ? " dim" : "") + (!c.dim && c.d === today ? " today" : "")}
              >
                <div className="dn">{c.d}</div>
                {posts &&
                  posts.map((p, j) => (
                    <div key={j} className="cal-post" draggable>
                      <span className="cal-pf-cluster">
                        {p.pfs.slice(0, 3).map((k) => (
                          <span key={k} className={"pf-dot " + PF[k].cls} style={{ width: 7, height: 7 }} />
                        ))}
                      </span>
                      <span className="tx">{p.t}</span>
                      <span className="tm">{p.tm}</span>
                    </div>
                  ))}
                {ghost && (
                  <div className="cal-ghost">
                    <Sparkle size={11} /> Suggested {ghost}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
