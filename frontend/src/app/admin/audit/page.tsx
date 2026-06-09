"use client";

import { useApi } from "@/lib/api/useApi";
import type { AdminAuditLog, Paginated } from "@/lib/api/types";

function formatDate(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function AdminAuditPage() {
  const { data, loading, error } = useApi<Paginated<AdminAuditLog>>("admin/audit?page=1&size=50");
  const rows = data?.items ?? [];

  return (
    <div className="view-pad">
      <div className="vh">
        <div className="vh-title">
          <h2>Audit log</h2>
          <p>{data ? `${data.total} events` : "-"}</p>
        </div>
      </div>

      <div className="posts-table">
        <div className="posts-row head" style={{ gridTemplateColumns: "180px minmax(0,1fr) 160px 140px" }}>
          <span>When</span>
          <span>Action</span>
          <span>Target</span>
          <span>IP</span>
        </div>
        {loading && <div className="posts-row"><span className="post-sub">Loading…</span></div>}
        {error && <div className="posts-row"><span className="post-sub">{error}</span></div>}
        {!loading && rows.length === 0 && <div className="posts-row"><span className="post-sub">No events yet.</span></div>}
        {rows.map((r) => (
          <div key={r.id} className="posts-row" style={{ gridTemplateColumns: "180px minmax(0,1fr) 160px 140px" }}>
            <span className="post-date">{formatDate(r.created_at)}</span>
            <span className="post-text" style={{ fontFamily: "var(--font-mono)", fontSize: 13 }}>{r.action}</span>
            <span className="post-sub">{r.target_type ? `${r.target_type}` : "-"}</span>
            <span className="post-sub">{r.ip ?? "-"}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
