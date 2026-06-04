"use client";

import { useState } from "react";

import { useApi } from "@/lib/api/useApi";
import type { AdminErrorLog, Paginated } from "@/lib/api/types";

function formatDate(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function AdminErrorsPage() {
  const { data, loading, error } = useApi<Paginated<AdminErrorLog>>("admin/errors?page=1&size=50");
  const [open, setOpen] = useState<string | null>(null);
  const rows = data?.items ?? [];

  return (
    <div className="view-pad">
      <div className="vh">
        <div className="vh-title">
          <h2>Error log</h2>
          <p>{data ? `${data.total} captured server errors` : "—"}</p>
        </div>
      </div>

      {loading && <div className="post-sub">Loading…</div>}
      {error && <div className="post-sub">{error}</div>}
      {!loading && rows.length === 0 && (
        <div className="post-sub">No server errors logged. That&apos;s a good sign. ✨</div>
      )}

      {rows.length > 0 && (
        <table className="errlog">
          <thead>
            <tr>
              <th>When</th>
              <th>Status</th>
              <th>Endpoint</th>
              <th>Message</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id}>
                <td style={{ whiteSpace: "nowrap" }}>{formatDate(r.created_at)}</td>
                <td>
                  <span className={"err-pill s" + Math.floor(r.status_code / 100)}>{r.status_code}</span>
                </td>
                <td>
                  <code>
                    {r.method} {r.path}
                  </code>
                </td>
                <td>
                  <button
                    className="link"
                    style={{ background: "none", border: "none", cursor: "pointer", padding: 0, textAlign: "left" }}
                    onClick={() => setOpen(open === r.id ? null : r.id)}
                  >
                    {r.message}
                  </button>
                  {open === r.id && r.stack && <pre className="err-stack">{r.stack}</pre>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
