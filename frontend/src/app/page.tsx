// "use client";

// import Link from "next/link";
// import { useState } from "react";
// import { motion } from "framer-motion";

// import { LandingIconSprite } from "@/components/landing/LandingIconSprite";
// import { LandingNav } from "@/components/landing/LandingNav";
// import { LandingFooter } from "@/components/landing/LandingFooter";
// import { HeroDemo } from "@/components/landing/HeroDemo";
// import { PricingContent } from "@/components/landing/PricingContent";
// import { ProductMock } from "@/components/landing/ProductMock";
// import { PlatformLogo } from "@/components/PlatformLogo";
// import { Icon } from "@/components/Icon";
// import { useApi } from "@/lib/api/useApi";
// import { fadeUp, revealOnView, staggerContainer } from "@/lib/motion";
// import type { SiteContent } from "@/lib/api/types";

// import "@/styles/landing.css";

// const PLATFORMS = [
//   "facebook", "instagram", "threads", "linkedin", "x", "youtube", "tiktok", "blogger", "wordpress",
// ] as const;

// // Map a feature's icon (from the site CMS) to a category label + product-mock visual,
// // so the badge and illustration always match the feature's meaning.
// const FEATURE_META: Record<string, { tag: string; variant: "compose" | "ai" | "calendar" | "connections" }> = {
//   compose: { tag: "Compose", variant: "compose" },
//   calendar: { tag: "Schedule", variant: "calendar" },
//   analytics: { tag: "Analytics", variant: "ai" },
//   shield: { tag: "Brand voice", variant: "ai" },
//   connections: { tag: "Connections", variant: "connections" },
// };
// const featureMeta = (icon: string) => FEATURE_META[icon] ?? { tag: "Feature", variant: "compose" as const };

// export default function LandingPage() {
//   const { data } = useApi<SiteContent>("site/content");
//   const [openFaq, setOpenFaq] = useState<number | null>(0);

//   const hero = data?.hero;
//   const logos = data?.logos ?? [];
//   const features = data?.features ?? [];
//   const testimonials = data?.testimonials ?? [];
//   const faq = data?.faq ?? [];
//   const announce = data?.announcement;
//   const showPricing = data?.flags?.show_pricing ?? true;

//   return (
//     <>
//       <LandingIconSprite />

//       {announce?.enabled && (
//         <div className="lp-announce">
//           <span>{announce.text}</span>
//           {announce.href && <Link href={announce.href}>Get started →</Link>}
//         </div>
//       )}

//       <LandingNav />

//       {/* ===== Hero ===== */}
//       <header className="hero lp-section lp-rhythm" style={{ paddingTop: 72 }}>
//         <div className="hero-grid paper-grid" />
//         <div className="hero-inner">
//           <motion.div className="hero-text" initial="hidden" animate="show" variants={staggerContainer(0.1)}>
//             <motion.div className="hero-eyebrow t-caption" variants={fadeUp}>
//               {hero?.eyebrow ?? "AI-Powered Social Autopilot"}
//             </motion.div>
//             <motion.h1 className="t-display-xl" variants={fadeUp}>
//               {hero ? (
//                 hero.title
//               ) : (
//                 <>
//                   Write it once.
//                   <br />
//                   <span className="postit-word">Postit</span> everywhere.
//                 </>
//               )}
//             </motion.h1>
//             <motion.p className="hero-sub t-body-l" variants={fadeUp}>
//               {hero?.subtitle ??
//                 "One idea in, nine native posts out. Postit's AI rewrites and reformats your post for every platform - then publishes on your schedule."}
//             </motion.p>
//             <motion.div className="hero-cta" variants={fadeUp}>
//               <Link href={hero?.primary_cta?.href ?? "/signup"} className="btn btn-spark btn-lg">
//                 {hero?.primary_cta?.label ?? "Start free - no card needed"}
//               </Link>
//               <Link href={hero?.secondary_cta?.href ?? "#how"} className="btn btn-ghost btn-lg">
//                 <Icon name="compose" size={18} /> {hero?.secondary_cta?.label ?? "See how it works"}
//               </Link>
//             </motion.div>
//             <motion.div className="trust-strip" variants={fadeUp}>
//               <div className="trust-logos">
//                 {PLATFORMS.map((p) => (
//                   <span key={p} className={`pf pf-${p}`}>
//                     <PlatformLogo platform={p} />
//                   </span>
//                 ))}
//               </div>
//               <span className="t-caption" style={{ textTransform: "none", letterSpacing: 0 }}>
//                 Connect all your accounts in minutes.
//               </span>
//             </motion.div>
//           </motion.div>

//           <motion.div
//             className="hero-demo-wrap"
//             style={{ position: "relative" }}
//             initial={{ opacity: 0, y: 24 }}
//             animate={{ opacity: 1, y: 0 }}
//             transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1], delay: 0.15 }}
//           >
//             <div className="sticky-peek" />
//             <HeroDemo />
//           </motion.div>
//         </div>
//       </header>

//       {/* ===== Social proof ===== */}
//       {logos.length > 0 && (
//         <section className="lp-section proof" style={{ padding: "48px 32px" }}>
//           <div className="proof-label t-body-s">Trusted by teams who post everywhere</div>
//           <div className="proof-row">
//             {logos.map((l) => (
//               <span key={l} className="proof-logo">
//                 {l}
//               </span>
//             ))}
//           </div>
//         </section>
//       )}

//       {/* ===== How it works ===== */}
//       <section className="lp-section lp-rhythm" id="how">
//         <motion.div className="how-head" {...revealOnView} variants={fadeUp}>
//           <div className="section-eyebrow" style={{ marginBottom: 14 }}>
//             How it works
//           </div>
//           <h2 className="t-h1">From one idea to everywhere, in three steps.</h2>
//         </motion.div>
//         <motion.div className="steps" {...revealOnView} variants={staggerContainer(0.12)}>
//           {[
//             { n: "01", v: "compose", t: "Write your idea", d: "Drop one post into a single clean composer." },
//             { n: "02", v: "ai", t: "AI makes it native", d: "Postit rewrites tone, length, hashtags and format for each platform." },
//             { n: "03", v: "calendar", t: "Publish or schedule", d: "Post once - it goes live everywhere, or queues for the perfect time." },
//           ].map((s) => (
//             <motion.div key={s.n} className="step-card" variants={fadeUp}>
//               <div className="step-num">{s.n}</div>
//               <div
//                 className="step-illus"
//                 style={{ height: "auto", padding: 0, background: "none", marginBottom: 20 }}
//               >
//                 <ProductMock variant={s.v as "compose"} />
//               </div>
//               <h3 className="t-h3">{s.t}</h3>
//               <p>{s.d}</p>
//             </motion.div>
//           ))}
//         </motion.div>
//       </section>

//       {/* ===== Feature deep-dives (from site content) ===== */}
//       <section className="lp-section lp-rhythm" id="features">
//         {features.map((f, i) => (
//           <motion.div
//             key={i}
//             className={"feat-row" + (i % 2 === 1 ? " reverse" : "")}
//             {...revealOnView}
//             variants={staggerContainer(0.1)}
//           >
//             <motion.div className="feat-text" variants={fadeUp}>
//               <span className="badge badge-spark">
//                 <span className="badge-dot" /> {featureMeta(f.icon).tag}
//               </span>
//               <h3>{f.title}</h3>
//               <p>{f.body}</p>
//             </motion.div>
//             <motion.div
//               className="feat-shot"
//               style={{ height: "auto", padding: 0, background: "none", border: "none", boxShadow: "none" }}
//               variants={fadeUp}
//             >
//               <ProductMock variant={featureMeta(f.icon).variant} />
//             </motion.div>
//           </motion.div>
//         ))}
//       </section>

//       {/* ===== Stats band ===== */}
//       <section className="lp-section" style={{ padding: "48px 32px" }}>
//         <motion.div className="stats-band" {...revealOnView} variants={fadeUp}>
//           <div className="stats-grid">
//             <div>
//               <div className="stat-num">9×</div>
//               <div className="stat-label">fewer copy-pastes</div>
//             </div>
//             <div>
//               <div className="stat-num">Minutes</div>
//               <div className="stat-label">not mornings</div>
//             </div>
//             <div>
//               <div className="stat-num">1</div>
//               <div className="stat-label">composer to rule them all</div>
//             </div>
//           </div>
//         </motion.div>
//       </section>

//       {/* ===== Testimonials ===== */}
//       {testimonials.length > 0 && (
//         <section className="lp-section lp-rhythm">
//           <motion.div className="tst-head" {...revealOnView} variants={fadeUp}>
//             <div className="section-eyebrow" style={{ marginBottom: 14 }}>
//               Loved by busy people
//             </div>
//             <h2 className="t-h1">The morning copy-paste ritual is over.</h2>
//           </motion.div>
//           <motion.div className="tst-grid" {...revealOnView} variants={staggerContainer(0.1)}>
//             {testimonials.map((t, i) => (
//               <motion.div key={i} className="tst-card" variants={fadeUp}>
//                 <p className="tst-quote">“{t.quote}”</p>
//                 <div className="tst-who">
//                   <div className="tst-avatar">
//                     {t.name.split(" ").map((p) => p[0]).slice(0, 2).join("")}
//                   </div>
//                   <div>
//                     <div className="tst-name">{t.name}</div>
//                     <div className="tst-role">{t.role}</div>
//                   </div>
//                 </div>
//               </motion.div>
//             ))}
//           </motion.div>
//         </section>
//       )}

//       {/* ===== Pricing ===== */}
//       {showPricing && <PricingContent />}

//       {/* ===== FAQ ===== */}
//       {faq.length > 0 && (
//         <section className="lp-section lp-rhythm">
//           <motion.div className="how-head" {...revealOnView} variants={fadeUp}>
//             <div className="section-eyebrow" style={{ marginBottom: 14 }}>
//               Questions
//             </div>
//             <h2 className="t-h1">Everything you might be wondering.</h2>
//           </motion.div>
//           <div className="lp-faq">
//             {faq.map((item, i) => (
//               <div key={i} className={"lp-faq-item" + (openFaq === i ? " open" : "")}>
//                 <button className="lp-faq-q" onClick={() => setOpenFaq(openFaq === i ? null : i)}>
//                   {item.q}
//                   <span className="chev">
//                     <Icon name="chevd" size={18} />
//                   </span>
//                 </button>
//                 {openFaq === i && <div className="lp-faq-a">{item.a}</div>}
//               </div>
//             ))}
//           </div>
//         </section>
//       )}

//       {/* ===== Final CTA ===== */}
//       <section className="lp-section">
//         <motion.div className="final-cta" {...revealOnView} variants={fadeUp}>
//           <div className="sticky-peek" />
//           <div className="sticky-peek two" />
//           <h2 className="t-display-l">Your next post is already nine posts.</h2>
//           <p className="sub">Write the idea once. Let Postit make it native everywhere.</p>
//           <Link href="/signup" className="btn btn-spark btn-lg">
//             Start free
//           </Link>
//           <p className="reassure t-body-s">Free forever plan · No credit card · Connect in minutes.</p>
//         </motion.div>
//       </section>

//       {/* ===== Footer ===== */}
//       <LandingFooter />
//     </>
//   );
// }


























// Hosting renew notic
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
