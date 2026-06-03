"use client";

import { useState } from "react";
import { Icon } from "@/components/Icon";
import { PF } from "@/lib/platforms";
import type { PlatformKey } from "@/lib/types";

const TREND = [
  { w: "Wk 1", v: 42 },
  { w: "Wk 2", v: 58 },
  { w: "Wk 3", v: 51 },
  { w: "Wk 4", v: 73 },
  { w: "Wk 5", v: 66 },
  { w: "Wk 6", v: 88 },
  { w: "Wk 7", v: 95 },
];

const PF_BREAK: Array<{ key: PlatformKey; val: number }> = [
  { key: "instagram", val: 38 },
  { key: "x", val: 26 },
  { key: "linkedin", val: 19 },
  { key: "threads", val: 11 },
  { key: "facebook", val: 6 },
];

export function Analytics() {
  const [range, setRange] = useState("30 days");
  const max = Math.max(...TREND.map((t) => t.v));

  return (
    <div className="view-pad">
      <div className="vh">
        <div className="vh-title">
          <h2>Analytics</h2>
          <p>Reach and engagement across every connected platform.</p>
        </div>
        <div className="vh-actions">
          <div className="seg">
            {["7 days", "30 days", "90 days"].map((r) => (
              <button key={r} className={range === r ? "on" : ""} onClick={() => setRange(r)}>
                {r}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="metric-grid">
        <div className="metric-card">
          <div className="metric-label">Total reach</div>
          <div className="metric-val">128.4k</div>
          <div className="metric-delta up">
            <Icon name="analytics" size={14} /> +18.2% vs last period
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Engagement rate</div>
          <div className="metric-val">4.7%</div>
          <div className="metric-delta up">
            <Icon name="analytics" size={14} /> +0.6 pts
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Posts published</div>
          <div className="metric-val">63</div>
          <div className="metric-delta up">
            <Icon name="analytics" size={14} /> 9× fewer copy-pastes
          </div>
        </div>
      </div>

      <div className="chart-card">
        <h3>Reach over time</h3>
        <div className="bars">
          {TREND.map((t, i) => (
            <div key={i} className="bar-col">
              <div className={"bar" + (i === TREND.length - 1 ? " spark" : "")} style={{ height: (t.v / max) * 100 + "%" }} />
              <div className="bar-label">{t.w}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="pf-break">
        <h3 style={{ fontSize: 17, marginBottom: 16 }}>Reach by platform</h3>
        {PF_BREAK.map((b) => (
          <div key={b.key} className="pf-break-row">
            <span className="nm">
              <span className={"pf-dot " + PF[b.key].cls} style={{ marginRight: 8, verticalAlign: "middle" }} />
              {PF[b.key].name}
            </span>
            <span className="pf-break-bar">
              <i style={{ width: b.val + "%", background: `var(--${PF[b.key].cls})` }} />
            </span>
            <span className="val">{b.val}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}
