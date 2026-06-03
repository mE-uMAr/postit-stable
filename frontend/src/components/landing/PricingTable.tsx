"use client";

import Link from "next/link";
import { useState } from "react";

type Cycle = "monthly" | "annual";

function Tick() {
  return (
    <svg className="tk" width="18" height="18">
      <use href="#i-check" />
    </svg>
  );
}

export function PricingTable() {
  const [cycle, setCycle] = useState<Cycle>("monthly");
  const proAmt = cycle === "annual" ? "$15" : "$19";
  const teamAmt = cycle === "annual" ? "$39" : "$49";

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
        <div className="price-card">
          <div className="price-name">Free</div>
          <div className="price-amt">
            $0<span> / forever</span>
          </div>
          <ul className="price-ticks">
            <li><Tick /> 3 connected accounts</li>
            <li><Tick /> 10 AI posts / month</li>
            <li><Tick /> Basic scheduling</li>
            <li><Tick /> 1 workspace</li>
          </ul>
          <Link href="/signup" className="btn btn-secondary btn-block">
            Start free
          </Link>
        </div>

        <div className="price-card featured">
          <div className="price-pop">Most popular</div>
          <div className="price-name">Pro</div>
          <div className="price-amt">
            {proAmt}
            <span> / month</span>
          </div>
          <ul className="price-ticks">
            <li><Tick /> All 9 platforms</li>
            <li><Tick /> Unlimited AI rewrites</li>
            <li><Tick /> Calendar, queue &amp; best-time</li>
            <li><Tick /> Brand voice &amp; analytics</li>
          </ul>
          <Link href="/signup" className="btn btn-spark btn-block">
            Start free trial
          </Link>
        </div>

        <div className="price-card">
          <div className="price-name">Team</div>
          <div className="price-amt">
            {teamAmt}
            <span> / month</span>
          </div>
          <ul className="price-ticks">
            <li><Tick /> Everything in Pro</li>
            <li><Tick /> 5 seats &amp; roles</li>
            <li><Tick /> Approval workflows</li>
            <li><Tick /> Shared brand voices</li>
          </ul>
          <Link href="/signup" className="btn btn-secondary btn-block">
            Start free
          </Link>
        </div>
      </div>
    </section>
  );
}
