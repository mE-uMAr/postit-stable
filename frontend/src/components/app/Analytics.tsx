"use client";

import { useEffect, useState } from "react";
import { Icon } from "@/components/Icon";
import { api } from "@/lib/api/client";
import { errorMessage } from "@/lib/api/useApi";
import type { ApiAnalytics } from "@/lib/api/types";

const RANGES: { label: string; days: number }[] = [
  { label: "7 days", days: 7 },
  { label: "30 days", days: 30 },
  { label: "90 days", days: 90 },
];

function humanize(n: number): string {
  if (n >= 1000) return (n / 1000).toFixed(1) + "k";
  return String(n);
}

export function Analytics() {
  const [days, setDays] = useState(30);
  const [data, setData] = useState<ApiAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    api
      .get<ApiAnalytics>(`analytics?range=${days}`)
      .then((res) => !cancelled && setData(res))
      .catch((e) => !cancelled && setError(errorMessage(e)))
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, [days]);

  const trend = data?.trend ?? [];
  const max = Math.max(1, ...trend.map((t) => t.value));

  return (
    <div className="view-pad">
      <div className="vh">
        <div className="vh-title">
          <h2>Analytics</h2>
          <p>Reach and engagement across every connected platform.</p>
        </div>
        <div className="vh-actions">
          <div className="seg">
            {RANGES.map((r) => (
              <button key={r.days} className={days === r.days ? "on" : ""} onClick={() => setDays(r.days)}>
                {r.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {loading && <div className="post-sub">Loading analytics…</div>}
      {error && <div className="post-sub">{error}</div>}

      {!loading && !error && data && (
        <>
          <div className="metric-grid">
            <div className="metric-card">
              <div className="metric-label">Total reach</div>
              <div className="metric-val">{humanize(data.overview.total_reach)}</div>
              <div className="metric-delta up">
                <Icon name="analytics" size={14} /> {data.overview.reach_delta.value}{" "}
                {data.overview.reach_delta.label}
              </div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Engagement rate</div>
              <div className="metric-val">{data.overview.engagement_rate}%</div>
              <div className="metric-delta up">
                <Icon name="analytics" size={14} /> {data.overview.engagement_delta.value}
              </div>
            </div>
            <div className="metric-card">
              <div className="metric-label">Posts published</div>
              <div className="metric-val">{data.overview.posts_published}</div>
              <div className="metric-delta up">
                <Icon name="analytics" size={14} /> {data.overview.posts_delta.value}{" "}
                {data.overview.posts_delta.label}
              </div>
            </div>
          </div>

          <div className="chart-card">
            <h3>Reach over time</h3>
            <div className="bars">
              {trend.map((t, i) => (
                <div key={i} className="bar-col">
                  <div
                    className={"bar" + (i === trend.length - 1 ? " spark" : "")}
                    style={{ height: (t.value / max) * 100 + "%" }}
                  />
                  <div className="bar-label">{t.label}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="pf-break">
            <h3 style={{ fontSize: 17, marginBottom: 16 }}>Reach by platform</h3>
            {data.by_platform.map((b) => (
              <div key={b.platform_id} className="pf-break-row">
                <span className="nm">
                  <span
                    className={"pf-dot pf-" + b.platform_id}
                    style={{ marginRight: 8, verticalAlign: "middle" }}
                  />
                  {b.name}
                </span>
                <span className="pf-break-bar">
                  <i style={{ width: b.percent + "%", background: b.color }} />
                </span>
                <span className="val">{b.percent}%</span>
              </div>
            ))}
            {data.by_platform.length === 0 && <div className="post-sub">No reach data yet.</div>}
          </div>
        </>
      )}
    </div>
  );
}
