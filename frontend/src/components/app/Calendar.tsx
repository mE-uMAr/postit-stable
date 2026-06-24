"use client";

import { useMemo, useState } from "react";
import { Icon } from "@/components/Icon";
import { Skeleton } from "@/components/ui/Skeleton";
import { useApi } from "@/lib/api/useApi";
import { PF } from "@/lib/platforms";
import type { ApiPost, Paginated } from "@/lib/api/types";
import type { PlatformKey } from "@/lib/types";

const DOW = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const MONTHS = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

interface Cell {
  d: number;
  dim: boolean;
  key: string; // YYYY-M-D for the in-month days
}

function buildMonth(year: number, month: number): Cell[] {
  const first = new Date(year, month, 1).getDay();
  const days = new Date(year, month + 1, 0).getDate();
  const prevDays = new Date(year, month, 0).getDate();
  const cells: Cell[] = [];
  for (let i = 0; i < first; i++) cells.push({ d: prevDays - first + i + 1, dim: true, key: "" });
  for (let d = 1; d <= days; d++) cells.push({ d, dim: false, key: `${year}-${month}-${d}` });
  while (cells.length % 7 !== 0) cells.push({ d: cells.length - first - days + 1, dim: true, key: "" });
  return cells;
}

function hhmm(iso: string): string {
  const d = new Date(iso);
  return `${d.getHours().toString().padStart(2, "0")}:${d.getMinutes().toString().padStart(2, "0")}`;
}

export function Calendar() {
  const now = new Date();
  const [cursor, setCursor] = useState({ y: now.getFullYear(), m: now.getMonth() });

  const postsRes = useApi<Paginated<ApiPost>>("posts?size=100");

  const cells = useMemo(() => buildMonth(cursor.y, cursor.m), [cursor]);
  const isThisMonth = cursor.y === now.getFullYear() && cursor.m === now.getMonth();

  // Posts history: published posts placed on their published date.
  const byDay = useMemo(() => {
    const map: Record<string, { id: string; t: string; tm: string; pfs: PlatformKey[]; status: string }[]> = {};
    for (const p of postsRes.data?.items ?? []) {
      if (!p.published_at) continue;
      const d = new Date(p.published_at);
      if (d.getFullYear() !== cursor.y || d.getMonth() !== cursor.m) continue;
      const key = `${cursor.y}-${cursor.m}-${d.getDate()}`;
      (map[key] ||= []).push({
        id: p.id,
        t: p.title,
        tm: hhmm(p.published_at),
        pfs: p.targets.map((t) => t.platform_id as PlatformKey),
        status: p.status,
      });
    }
    return map;
  }, [postsRes.data, cursor]);

  const move = (delta: number) => {
    setCursor((c) => {
      const m = c.m + delta;
      return { y: c.y + Math.floor(m / 12), m: ((m % 12) + 12) % 12 };
    });
  };

  const loading = postsRes.loading;

  return (
    <div className="view-pad">
      <div className="vh">
        <div className="vh-title">
          <h2>Calendar</h2>
          <p>Your posting history — published posts by day.</p>
        </div>
      </div>

      <div className="cal-wrap">
        <div className="cal-head">
          <div className="mo">
            {MONTHS[cursor.m]} {cursor.y}
          </div>
          <div className="cal-nav">
            <button onClick={() => move(-1)} title="Previous month">
              <Icon name="chevl" size={17} />
            </button>
            <button onClick={() => move(1)} title="Next month">
              <Icon name="chevr" size={17} />
            </button>
          </div>
        </div>

        {loading ? (
          <div style={{ padding: 16 }}>
            <Skeleton height={420} radius={14} />
          </div>
        ) : (
          <div className="cal-grid">
            {DOW.map((d) => (
              <div key={d} className="cal-dow">
                {d}
              </div>
            ))}
            {cells.map((c, i) => {
              const posts = !c.dim ? byDay[c.key] : undefined;
              const isToday = !c.dim && isThisMonth && c.d === now.getDate();
              return (
                <div
                  key={i}
                  className={"cal-cell" + (c.dim ? " dim" : "") + (isToday ? " today" : "")}
                >
                  <div className="dn">{c.d}</div>
                  {posts?.map((p, j) => (
                    <div key={j} className="cal-post" title={p.t}>
                      <span className="cal-pf-cluster">
                        {p.pfs.slice(0, 3).map((k) => (
                          <span
                            key={k}
                            className={"pf-dot " + (PF[k]?.cls ?? "")}
                            style={{ width: 7, height: 7 }}
                          />
                        ))}
                      </span>
                      <span className="tx">{p.t}</span>
                      <span className="tm">{p.tm}</span>
                    </div>
                  ))}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
