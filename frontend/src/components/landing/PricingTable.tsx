"use client";

import Link from "next/link";
import { useState } from "react";

import { useApi } from "@/lib/api/useApi";
import type { ApiPlan } from "@/lib/api/types";

type Cycle = "monthly" | "annual";

function Tick() {
  return (
    <svg className="tk" width="18" height="18">
      <use href="#i-check" />
    </svg>
  );
}

function priceLabel(plan: ApiPlan, cycle: Cycle): { amt: string; unit: string } {
  if (plan.price_monthly_cents === 0) return { amt: "$0", unit: " / forever" };
  const cents =
    cycle === "annual"
      ? Math.round(plan.price_annual_cents / 12)
      : plan.price_monthly_cents;
  return { amt: "$" + (cents / 100).toFixed(0), unit: " / month" };
}

export function PricingTable() {
  const [cycle, setCycle] = useState<Cycle>("monthly");
  const { data, loading } = useApi<ApiPlan[]>("subscriptions/plans");
  const plans = (data ?? []).filter((p) => p.is_public).sort((a, b) => a.sort_order - b.sort_order);
  const featuredCode = plans.find((p) => p.code === "pro")?.code ?? plans[1]?.code;

  return (
    <section className="lp-section lp-rhythm" id="pricing">
      <div className="price-head">
        <div className="section-eyebrow" style={{ marginBottom: 14 }}>
          Pricing
        </div>
        <h2 className="t-h1">Start free. Upgrade when it pays for itself.</h2>
      </div>

      <div className="price-toggle">
        <div className="toggle-pill" id="priceToggle">
          <button className={cycle === "monthly" ? "on" : ""} onClick={() => setCycle("monthly")}>
            Monthly
          </button>
          <button className={cycle === "annual" ? "on" : ""} onClick={() => setCycle("annual")}>
            Annual · save 20%
          </button>
        </div>
      </div>

      <div className="price-grid">
        {loading && plans.length === 0 &&
          [0, 1, 2].map((i) => <div key={i} className="price-card sk" style={{ height: 360 }} />)}
        {plans.map((plan) => {
          const { amt, unit } = priceLabel(plan, cycle);
          const featured = plan.code === featuredCode;
          return (
            <div key={plan.id} className={"price-card" + (featured ? " featured" : "")}>
              {featured && <div className="price-pop">Most popular</div>}
              <div className="price-name">{plan.name}</div>
              <div className="price-amt">
                {amt}
                <span>{unit}</span>
              </div>
              <ul className="price-ticks">
                {plan.features.map((f, i) => (
                  <li key={i}>
                    <Tick /> {f}
                  </li>
                ))}
              </ul>
              <Link
                href="/signup"
                className={"btn btn-block " + (featured ? "btn-spark" : "btn-secondary")}
              >
                {plan.price_monthly_cents === 0 ? "Start free" : "Start free trial"}
              </Link>
            </div>
          );
        })}
      </div>
    </section>
  );
}
