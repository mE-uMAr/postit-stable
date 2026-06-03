"use client";

import { useApi } from "@/lib/api/useApi";
import type { AdminMetrics } from "@/lib/api/types";

function money(cents: number): string {
  return "$" + (cents / 100).toLocaleString(undefined, { maximumFractionDigits: 0 });
}

export default function AdminDashboard() {
  const { data, loading, error } = useApi<AdminMetrics>("admin/metrics");

  return (
    <div className="view-pad">
      <div className="vh">
        <div className="vh-title">
          <h2>Overview</h2>
          <p>Platform-wide health across users, workspaces, and revenue.</p>
        </div>
      </div>

      {loading && <div className="post-sub">Loading metrics…</div>}
      {error && <div className="post-sub">{error}</div>}

      {data && (
        <>
          <div className="metric-grid">
            <Metric label="Total users" value={String(data.total_users)} sub={`${data.new_users_30d} new in 30d`} />
            <Metric label="Active workspaces" value={String(data.active_workspaces)} sub={`${data.total_workspaces} total`} />
            <Metric label="MRR" value={money(data.mrr_cents)} sub={`${money(data.arr_cents)} ARR`} />
          </div>
          <div className="metric-grid">
            <Metric label="Paying subscriptions" value={String(data.paying_subscriptions)} sub="active paid" />
            <Metric label="Posts" value={String(data.total_posts)} sub={`${data.posts_published} published`} />
            <Metric label="Active users" value={String(data.active_users)} sub="not disabled" />
          </div>

          <div className="pf-break" style={{ marginTop: 24 }}>
            <h3 style={{ fontSize: 17, marginBottom: 16 }}>Plan distribution</h3>
            {Object.entries(data.plan_distribution).map(([name, count]) => {
              const total = Object.values(data.plan_distribution).reduce((a, b) => a + b, 0) || 1;
              return (
                <div key={name} className="pf-break-row">
                  <span className="nm">{name}</span>
                  <span className="pf-break-bar">
                    <i style={{ width: (count / total) * 100 + "%", background: "var(--ai)" }} />
                  </span>
                  <span className="val">{count}</span>
                </div>
              );
            })}
            {Object.keys(data.plan_distribution).length === 0 && <div className="post-sub">No subscriptions yet.</div>}
          </div>
        </>
      )}
    </div>
  );
}

function Metric({ label, value, sub }: { label: string; value: string; sub: string }) {
  return (
    <div className="metric-card">
      <div className="metric-label">{label}</div>
      <div className="metric-val">{value}</div>
      <div className="metric-delta up">{sub}</div>
    </div>
  );
}
