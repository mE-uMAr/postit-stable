"use client";

import type { ReactNode } from "react";

type HostingExpiredProps = {
  /** Plan name shown in the invoice row, e.g. "Standard Hosting — 6 months" */
  plan?: string;
  /** Amount due, pre-formatted, e.g. "Rs 4,500" */
  amount?: string;
  /** Duration text used in the CTA button, e.g. "6 months" */
  duration?: string;
  /** Days of uptime shown in the status log's "ok" line */
  uptimeDays?: number;
  /** Called when the pay button is clicked. If omitted, the button is a plain link to payHref. */
  onPay?: () => void;
  /** Used as the pay button's href when onPay isn't provided */
  payHref?: string;
  /** Support link href */
  supportHref?: string;
};

/**
 * Terminal/status-console styled notice shown when a hosting plan has expired.
 * Self-contained — styles are scoped via styled-jsx, no external CSS needed
 * beyond the Google Fonts import.
 */
export function HostingExpired({
  plan = "Standard Hosting — 6 months",
  amount = "Rs 4,500",
  duration = "6 months",
  uptimeDays = 179,
  onPay,
  payHref = "#",
  supportHref = "#",
}: HostingExpiredProps) {
  const ctaProps = onPay
    ? { as: "button" as const, onClick: onPay }
    : { as: "a" as const, href: payHref };

  return (
    <div className="hx-wrap">
      <div className="hx-card">
        <div className="hx-console-bar">
          <div className="hx-console-dots">
            <span />
            <span />
            <span />
          </div>
          <div className="hx-console-label">svc-status // hosting.uptime</div>
        </div>

        <div className="hx-status-log">
          <div className="hx-line">
            [boot] checking service <span className="hx-dim">web-01, db-01, mail-01</span>
          </div>
          <div className="hx-line hx-ok">[ok] all systems nominal — {uptimeDays} days uptime</div>
          <div className="hx-line hx-fail">[fail] billing cycle ended — service held for renewal</div>
          <div className="hx-line hx-dim">[info] awaiting payment to resume</div>
        </div>

        <div className="hx-body">
          <div className="hx-pill">
            <span className="hx-dot" />
            Hosting expired
          </div>

          <h1 className="hx-h1">Your hosting plan has expired.</h1>
          <p className="hx-subtext">
            Your site and its services are currently paused. Renew now to bring everything back
            online — nothing changes on your end once payment clears.
          </p>

          <div className="hx-invoice">
            <div className="hx-row">
              <span className="hx-k">Plan</span>
              <span className="hx-v">{plan}</span>
            </div>
            <div className="hx-row">
              <span className="hx-k">Status</span>
              <span className="hx-v hx-mono hx-status-down">EXPIRED</span>
            </div>
            <div className="hx-row hx-total">
              <span className="hx-k">Amount due</span>
              <span className="hx-v">{amount}</span>
            </div>
          </div>

          {ctaProps.as === "button" ? (
            <button className="hx-cta" onClick={ctaProps.onClick}>
              Pay {amount} to renew for {duration}
            </button>
          ) : (
            <a className="hx-cta" href={ctaProps.href}>
              Pay {amount} to renew for {duration}
            </a>
          )}

          <p className="hx-fine-print">
            Service resumes automatically within minutes of payment confirmation.
            <br />
            Questions about this invoice?{" "}
            <a href={supportHref} className="hx-support-link">
              Contact support
            </a>
          </p>
        </div>
      </div>

      <style jsx>{`
        .hx-wrap {
          --hx-bg: #0b0e11;
          --hx-panel: #12161b;
          --hx-border: #232a32;
          --hx-text-primary: #e6e9ec;
          --hx-text-muted: #7c8891;
          --hx-status-down: #e5484d;
          --hx-status-down-dim: #4a2224;
          --hx-status-up: #3dd68c;
          --hx-accent: #f2a544;

          width: 100%;
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 24px;
          background: var(--hx-bg);
          background-image: radial-gradient(circle at 15% 10%, rgba(229, 72, 77, 0.06), transparent 40%),
            radial-gradient(circle at 85% 90%, rgba(61, 214, 140, 0.03), transparent 40%);
          font-family: "Inter", sans-serif;
          color: var(--hx-text-primary);
        }

        .hx-card {
          width: 100%;
          max-width: 560px;
          background: var(--hx-panel);
          border: 1px solid var(--hx-border);
          border-radius: 10px;
          overflow: hidden;
          box-shadow: 0 40px 80px -20px rgba(0, 0, 0, 0.6);
        }

        .hx-console-bar {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 12px 18px;
          background: #0e1216;
          border-bottom: 1px solid var(--hx-border);
        }

        .hx-console-dots {
          display: flex;
          gap: 7px;
        }
        .hx-console-dots span {
          width: 10px;
          height: 10px;
          border-radius: 50%;
          background: #2a323a;
        }

        .hx-console-label {
          font-family: "JetBrains Mono", monospace;
          font-size: 11px;
          color: var(--hx-text-muted);
          letter-spacing: 0.04em;
        }

        .hx-status-log {
          font-family: "JetBrains Mono", monospace;
          font-size: 12.5px;
          line-height: 1.9;
          padding: 20px 24px;
          background: #0e1216;
          border-bottom: 1px solid var(--hx-border);
        }

        .hx-line {
          color: var(--hx-text-muted);
        }
        .hx-ok {
          color: var(--hx-status-up);
        }
        .hx-fail {
          color: var(--hx-status-down);
          font-weight: 700;
        }
        .hx-dim {
          color: #4a535c;
        }

        .hx-body {
          padding: 36px 32px 32px;
        }

        .hx-pill {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          padding: 6px 12px;
          border-radius: 100px;
          background: var(--hx-status-down-dim);
          border: 1px solid rgba(229, 72, 77, 0.35);
          font-family: "JetBrains Mono", monospace;
          font-size: 11.5px;
          font-weight: 500;
          color: var(--hx-status-down);
          letter-spacing: 0.03em;
          text-transform: uppercase;
          margin-bottom: 22px;
        }

        .hx-dot {
          width: 6px;
          height: 6px;
          border-radius: 50%;
          background: var(--hx-status-down);
          box-shadow: 0 0 0 3px rgba(229, 72, 77, 0.2);
        }

        .hx-h1 {
          font-size: 26px;
          font-weight: 800;
          letter-spacing: -0.01em;
          line-height: 1.25;
          margin: 0 0 10px;
        }

        .hx-subtext {
          color: var(--hx-text-muted);
          font-size: 14.5px;
          line-height: 1.6;
          margin: 0 0 28px;
          max-width: 46ch;
        }

        .hx-invoice {
          border: 1px solid var(--hx-border);
          border-radius: 8px;
          overflow: hidden;
          margin-bottom: 28px;
        }

        .hx-row {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 14px 18px;
          font-size: 13.5px;
        }

        .hx-row + .hx-row {
          border-top: 1px solid var(--hx-border);
        }

        .hx-k {
          color: var(--hx-text-muted);
        }
        .hx-v {
          font-weight: 500;
        }
        .hx-mono {
          font-family: "JetBrains Mono", monospace;
        }
        .hx-status-down {
          color: var(--hx-status-down);
        }

        .hx-total {
          background: #161b21;
        }
        .hx-total .hx-k {
          color: var(--hx-text-primary);
          font-weight: 600;
        }
        .hx-total .hx-v {
          font-family: "JetBrains Mono", monospace;
          font-size: 18px;
          font-weight: 700;
          color: var(--hx-accent);
        }

        .hx-cta {
          display: block;
          width: 100%;
          text-align: center;
          background: var(--hx-accent);
          color: #1a1300;
          font-weight: 700;
          font-size: 15px;
          padding: 15px;
          border-radius: 8px;
          text-decoration: none;
          border: none;
          cursor: pointer;
          transition: filter 0.15s ease, transform 0.15s ease;
          font-family: inherit;
        }

        .hx-cta:hover {
          filter: brightness(1.08);
          transform: translateY(-1px);
        }
        .hx-cta:focus-visible {
          outline: 2px solid #fff;
          outline-offset: 3px;
        }

        .hx-fine-print {
          margin-top: 16px;
          font-size: 12px;
          color: #566069;
          text-align: center;
          line-height: 1.6;
        }

        .hx-support-link {
          color: var(--hx-text-muted);
          text-decoration: underline;
        }

        @media (max-width: 480px) {
          .hx-h1 {
            font-size: 22px;
          }
          .hx-body {
            padding: 28px 22px 26px;
          }
        }

        @media (prefers-reduced-motion: no-preference) {
          .hx-dot {
            animation: hx-pulse 1.8s ease-in-out infinite;
          }
        }
        @keyframes hx-pulse {
          0%,
          100% {
            opacity: 1;
          }
          50% {
            opacity: 0.4;
          }
        }
      `}</style>
    </div>
  );
}

export default HostingExpired;
