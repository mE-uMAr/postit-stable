"use client";

import { useMemo, useState } from "react";
import { Icon } from "@/components/Icon";
import { Sparkle } from "@/components/Sparkle";
import { Skeleton } from "@/components/ui/Skeleton";
import { useWorkspace } from "@/components/app/providers/WorkspaceProvider";
import { useToast } from "./providers/ToastProvider";
import { api } from "@/lib/api/client";
import { useApi, errorMessage } from "@/lib/api/useApi";
import { PF } from "@/lib/platforms";
import type { BestTime, ApiPost, Paginated } from "@/lib/api/types";
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
  const { canEdit } = useWorkspace();
  const pushToast = useToast();

  const postsRes = useApi<Paginated<ApiPost>>("posts?size=100");
  const bestRes = useApi<BestTime[]>("analytics/best-times");
  const [dragId, setDragId] = useState<string | null>(null);

  const cells = useMemo(() => buildMonth(cursor.y, cursor.m), [cursor]);
  const isThisMonth = cursor.y === now.getFullYear() && cursor.m === now.getMonth();

  // Index scheduled+published posts by day for the visible month.
  const byDay = useMemo(() => {
    const map: Record<string, { id: string; t: string; tm: string; pfs: PlatformKey[]; status: string }[]> = {};
    for (const p of postsRes.data?.items ?? []) {
      const iso = p.scheduled_at ?? p.published_at;
      if (!iso) continue;
      const d = new Date(iso);
      if (d.getFullYear() !== cursor.y || d.getMonth() !== cursor.m) continue;
      const key = `${cursor.y}-${cursor.m}-${d.getDate()}`;
      (map[key] ||= []).push({
        id: p.id,
        t: p.title,
        tm: hhmm(iso),
        pfs: p.targets.map((t) => t.platform_id as PlatformKey),
        status: p.status,
      });
    }
    return map;
  }, [postsRes.data, cursor]);

  // Ghost (AI best-time) slots, indexed by day for the visible month.
  const ghosts = useMemo(() => {
    const map: Record<string, string> = {};
    for (const b of bestRes.data ?? []) {
      const d = new Date(b.datetime);
      if (d.getFullYear() !== cursor.y || d.getMonth() !== cursor.m) continue;
      map[`${cursor.y}-${cursor.m}-${d.getDate()}`] = hhmm(b.datetime);
    }
    return map;
  }, [bestRes.data, cursor]);

  const move = (delta: number) => {
    setCursor((c) => {
      const m = c.m + delta;
      return { y: c.y + Math.floor(m / 12), m: ((m % 12) + 12) % 12 };
    });
  };

  const onDrop = async (cell: Cell) => {
    if (!dragId || cell.dim || !canEdit) return;
    const post = (postsRes.data?.items ?? []).find((p) => p.id === dragId);
    setDragId(null);
    if (!post) return;
    const src = new Date(post.scheduled_at ?? post.published_at ?? Date.now());
    const target = new Date(cursor.y, cursor.m, cell.d, src.getHours(), src.getMinutes());
    try {
      await api.post(`posts/${post.id}/schedule`, { scheduled_at: target.toISOString() });
      pushToast(`Rescheduled to ${MONTHS[cursor.m]} ${cell.d}`);
      await postsRes.reload();
    } catch (e) {
      pushToast(errorMessage(e));
    }
  };

  const loading = postsRes.loading;

  return (
    <div className="view-pad">
      <div className="vh">
        <div className="vh-title">
          <h2>Calendar</h2>
          <p>
            {canEdit ? "Drag posts to reschedule. " : ""}Ghost slots are AI best-time suggestions.
          </p>
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
          <span className="spacer" />
          <span className="pill">
            <span className="badge-dot" style={{ background: "var(--ai)" }} /> AI best-time
          </span>
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
              const ghost = !c.dim ? ghosts[c.key] : undefined;
              const isToday = !c.dim && isThisMonth && c.d === now.getDate();
              return (
                <div
                  key={i}
                  className={"cal-cell" + (c.dim ? " dim" : "") + (isToday ? " today" : "")}
                  onDragOver={(e) => {
                    if (dragId && !c.dim) e.preventDefault();
                  }}
                  onDrop={() => void onDrop(c)}
                >
                  <div className="dn">{c.d}</div>
                  {posts?.map((p, j) => (
                    <div
                      key={j}
                      className="cal-post"
                      draggable={canEdit}
                      onDragStart={() => setDragId(p.id)}
                      onDragEnd={() => setDragId(null)}
                      title={p.t}
                    >
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
                  {ghost && (
                    <div className="cal-ghost">
                      <Sparkle size={11} /> Suggested {ghost}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
