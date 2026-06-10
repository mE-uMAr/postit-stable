"use client";

import Link from "next/link";
import { useState } from "react";

import { Icon } from "@/components/Icon";
import { useApi } from "@/lib/api/useApi";
import type { ApiPlan, PricingConfig, SiteContent } from "@/lib/api/types";

type Cycle = "monthly" | "annual";

function Tick() {
  return (
    <svg className="tk" width="18" height="18">
      <use href="#i-check" />
    </svg>
  );
}

function rate(cents: number, currency: string): string {
  const symbol = currency === "USD" ? "$" : "";
  const dollars = cents / 100;
  return symbol + (Number.isInteger(dollars) ? dollars.toFixed(0) : dollars.toFixed(2));
}

function planPrice(plan: ApiPlan, cycle: Cycle): { amt: string; unit: string } {
  if (plan.price_monthly_cents === 0) return { amt: "$0", unit: " / forever" };
  const cents = cycle === "annual" ? Math.round(plan.price_annual_cents / 12) : plan.price_monthly_cents;
  return { amt: "$" + (cents / 100).toFixed(0), unit: " / month" };
}

/** Plan tiers or usage rates, driven by the admin-set pricing model in site content. */
export function PricingContent() {
  const site = useApi<SiteContent>("site/content");
  const plansRes = useApi<ApiPlan[]>("subscriptions/plans");
  const [cycle, setCycle] = useState<Cycle>("monthly");

  const pricing: PricingConfig | undefined = site.data?.pricing;
  const model = pricing?.model ?? "plan";
  const currency = pricing?.currency ?? "USD";

  return (
    <section className="lp-section lp-rhythm" id="pricing">
      <div className="price-head">
        <div className="section-eyebrow" style={{ marginBottom: 14 }}>
          Pricing
        </div>
        <h2 className="t-h1">{pricing?.headline ?? "Start free. Upgrade when it pays for itself."}</h2>
        {pricing?.subhead && (
          <p className="t-body-l" style={{ color: "var(--ink-soft)", marginTop: 12 }}>
            {pricing.subhead}
          </p>
        )}
      </div>

      {model === "usage" ? (
        <UsagePricing pricing={pricing!} currency={currency} />
      ) : (
        <PlanPricing
          plans={plansRes.data ?? []}
          loading={plansRes.loading}
          cycle={cycle}
          setCycle={setCycle}
        />
      )}
    </section>
  );
}

function PlanPricing({
  plans,
  loading,
  cycle,
  setCycle,
}: {
  plans: ApiPlan[];
  loading: boolean;
  cycle: Cycle;
  setCycle: (c: Cycle) => void;
}) {
  const visible = plans.filter((p) => p.is_public).sort((a, b) => a.sort_order - b.sort_order);
  const featured = visible.find((p) => p.code === "pro")?.code ?? visible[1]?.code;

  return (
    <>
      <div className="price-toggle">
        <div className="toggle-pill">
          <button className={cycle === "monthly" ? "on" : ""} onClick={() => setCycle("monthly")}>
            Monthly
          </button>
          <button className={cycle === "annual" ? "on" : ""} onClick={() => setCycle("annual")}>
            Annual · save 20%
          </button>
        </div>
      </div>
      <div className="price-grid">
        {loading && visible.length === 0 && [0, 1, 2].map((i) => <div key={i} className="price-card sk" style={{ height: 360 }} />)}
        {visible.map((plan) => {
          const { amt, unit } = planPrice(plan, cycle);
          const isFeatured = plan.code === featured;
          return (
            <div key={plan.id} className={"price-card" + (isFeatured ? " featured" : "")}>
              {isFeatured && <div className="price-pop">Most popular</div>}
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
              <Link href="/signup" className={"btn btn-block " + (isFeatured ? "btn-spark" : "btn-secondary")}>
                {plan.price_monthly_cents === 0 ? "Start free" : "Start free trial"}
              </Link>
            </div>
          );
        })}
      </div>
    </>
  );
}

function UsagePricing({ pricing, currency }: { pricing: PricingConfig; currency: string }) {
  const items = [
    { label: "Per published post", value: pricing.rates.per_post_cents, hint: "Each post that goes live to a platform." },
    { label: "Per AI generation", value: pricing.rates.per_ai_generation_cents, hint: "Each AI rewrite for a platform." },
    { label: "Per manual post", value: pricing.rates.per_manual_post_cents, hint: "Manual post creation and media upload." },
  ];
  return (
    <>
      <div className="price-grid">
        {items.map((it) => (
          <div key={it.label} className="price-card">
            <div className="price-name">{it.label}</div>
            <div className="price-amt">
              {rate(it.value, currency)}
              <span> / each</span>
            </div>
            <ul className="price-ticks">
              <li>
                <Tick /> {it.hint}
              </li>
              <li>
                <Tick /> No monthly commitment
              </li>
              <li>
                <Tick /> Billed at the end of each month
              </li>
            </ul>
          </div>
        ))}
      </div>
      <p className="reassure t-body-s" style={{ textAlign: "center", marginTop: 24 }}>
        <Icon name="check" size={15} /> {pricing.usage_note}
      </p>
      <div style={{ textAlign: "center", marginTop: 20 }}>
        <Link href="/signup" className="btn btn-spark btn-lg">
          Start free
        </Link>
      </div>
    </>
  );
}
