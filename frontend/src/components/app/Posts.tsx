"use client";

import { useState } from "react";
import { Icon } from "@/components/Icon";
import { PlatformLogo } from "@/components/PlatformLogo";
import { PF } from "@/lib/platforms";
import type { PlatformKey } from "@/lib/types";

type PostStatusValue = "scheduled" | "published" | "failed";

interface HistoryItem {
  t: string;
  sub: string;
  pfs: PlatformKey[];
  date: string;
  status: PostStatusValue;
}

const HISTORY: HistoryItem[] = [
  { t: "Launching our spring collection — lighter materials and a brighter palette", sub: "Generated · 4 variants", pfs: ["x", "linkedin", "instagram", "threads"], date: "Jun 3, 9:00", status: "scheduled" },
  { t: "Behind the scenes of this season's photo shoot", sub: "Generated · 2 variants", pfs: ["instagram", "threads"], date: "Jun 5, 12:30", status: "scheduled" },
  { t: "Customer spotlight: how the Alvarez family styles their space", sub: "Edited · 2 variants", pfs: ["linkedin", "facebook"], date: "Jun 9, 8:00", status: "scheduled" },
  { t: "Five small ways to refresh a room for spring", sub: "Published · 3 variants", pfs: ["x", "linkedin", "wordpress"], date: "May 28, 9:12", status: "published" },
  { t: "We hit 4,000 happy customers this week 🎉", sub: "Published · 5 variants", pfs: ["x", "instagram", "threads", "facebook", "linkedin"], date: "May 24, 17:40", status: "published" },
  { t: "New short: the making of our oak side table", sub: "Published · 2 variants", pfs: ["youtube", "tiktok"], date: "May 21, 15:00", status: "published" },
  { t: "Restock alert — the bestseller lamp is back", sub: "Failed · YouTube token expired", pfs: ["x", "instagram", "youtube"], date: "May 19, 9:00", status: "failed" },
];

function PostStatus({ s }: { s: PostStatusValue }) {
  if (s === "scheduled")
    return (
      <span className="badge badge-ai">
        <Icon name="clock" size={12} /> Scheduled
      </span>
    );
  if (s === "published")
    return (
      <span className="badge badge-success">
        <span className="badge-dot" /> Published
      </span>
    );
  return (
    <span className="badge badge-danger">
      <Icon name="alert" size={12} /> Failed
    </span>
  );
}

export function Posts() {
  const [filter, setFilter] = useState("All");
  const filters = ["All", "Scheduled", "Published", "Failed"];
  const rows = HISTORY.filter((h) => filter === "All" || h.status === filter.toLowerCase());

  return (
    <div className="view-pad">
      <div className="vh">
        <div className="vh-title">
          <h2>Posts</h2>
          <p>Everything you&apos;ve scheduled and published, across every platform.</p>
        </div>
        <div className="vh-actions">
          <div className="seg">
            {filters.map((f) => (
              <button key={f} className={filter === f ? "on" : ""} onClick={() => setFilter(f)}>
                {f}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="posts-table">
        <div className="posts-row head">
          <span>Post</span>
          <span>Platforms</span>
          <span>Date</span>
          <span>Status</span>
          <span />
        </div>
        {rows.map((r, i) => (
          <div key={i} className="posts-row">
            <div className="post-content">
              <span className="post-text">{r.t}</span>
              <span className="post-sub">{r.sub}</span>
            </div>
            <div className="post-pfs">
              {r.pfs.map((k) => (
                <span key={k} className={"pf " + PF[k].cls} style={{ width: 24, height: 24, borderRadius: 7, fontSize: 11 }}>
                  <PlatformLogo platform={k} />
                </span>
              ))}
            </div>
            <span className="post-date">{r.date}</span>
            <PostStatus s={r.status} />
            <button className="icon-btn" style={{ width: 34, height: 34, border: 0 }} title="More">
              <Icon name="dots" size={18} />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
