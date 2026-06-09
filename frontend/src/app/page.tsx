"use client";

import Link from "next/link";
import { useState } from "react";
import { motion } from "framer-motion";

import { LandingIconSprite } from "@/components/landing/LandingIconSprite";
import { LandingNav } from "@/components/landing/LandingNav";
import { HeroDemo } from "@/components/landing/HeroDemo";
import { PricingTable } from "@/components/landing/PricingTable";
import { ProductMock } from "@/components/landing/ProductMock";
import { PlatformLogo } from "@/components/PlatformLogo";
import { Icon } from "@/components/Icon";
import { useApi } from "@/lib/api/useApi";
import { fadeUp, revealOnView, staggerContainer } from "@/lib/motion";
import type { SiteContent } from "@/lib/api/types";

import "@/styles/landing.css";

const PLATFORMS = [
  "facebook", "instagram", "threads", "linkedin", "x", "youtube", "tiktok", "blogger", "wordpress",
] as const;

// Map a feature's icon (from the site CMS) to a category label + product-mock visual,
// so the badge and illustration always match the feature's meaning.
const FEATURE_META: Record<string, { tag: string; variant: "compose" | "ai" | "calendar" | "connections" }> = {
  compose: { tag: "Compose", variant: "compose" },
  calendar: { tag: "Schedule", variant: "calendar" },
  analytics: { tag: "Analytics", variant: "ai" },
  shield: { tag: "Brand voice", variant: "ai" },
  connections: { tag: "Connections", variant: "connections" },
};
const featureMeta = (icon: string) => FEATURE_META[icon] ?? { tag: "Feature", variant: "compose" as const };

export default function LandingPage() {
  const { data } = useApi<SiteContent>("site/content");
  const [openFaq, setOpenFaq] = useState<number | null>(0);

  const hero = data?.hero;
  const logos = data?.logos ?? [];
  const features = data?.features ?? [];
  const testimonials = data?.testimonials ?? [];
  const faq = data?.faq ?? [];
  const announce = data?.announcement;
  const showPricing = data?.flags?.show_pricing ?? true;

  return (
    <>
      <LandingIconSprite />

      {announce?.enabled && (
        <div className="lp-announce">
          <span>{announce.text}</span>
          {announce.href && <Link href={announce.href}>Get started →</Link>}
        </div>
      )}

      <LandingNav />

      {/* ===== Hero ===== */}
      <header className="hero lp-section lp-rhythm" style={{ paddingTop: 72 }}>
        <div className="hero-grid paper-grid" />
        <div className="hero-inner">
          <motion.div className="hero-text" initial="hidden" animate="show" variants={staggerContainer(0.1)}>
            <motion.div className="hero-eyebrow t-caption" variants={fadeUp}>
              {hero?.eyebrow ?? "AI-Powered Social Autopilot"}
            </motion.div>
            <motion.h1 className="t-display-xl" variants={fadeUp}>
              {hero ? (
                hero.title
              ) : (
                <>
                  Write it once.
                  <br />
                  <span className="postit-word">Postit</span> everywhere.
                </>
              )}
            </motion.h1>
            <motion.p className="hero-sub t-body-l" variants={fadeUp}>
              {hero?.subtitle ??
                "One idea in, nine native posts out. Postit's AI rewrites and reformats your post for every platform — then publishes on your schedule."}
            </motion.p>
            <motion.div className="hero-cta" variants={fadeUp}>
              <Link href={hero?.primary_cta?.href ?? "/signup"} className="btn btn-spark btn-lg">
                {hero?.primary_cta?.label ?? "Start free — no card needed"}
              </Link>
              <Link href={hero?.secondary_cta?.href ?? "#how"} className="btn btn-ghost btn-lg">
                <Icon name="compose" size={18} /> {hero?.secondary_cta?.label ?? "See how it works"}
              </Link>
            </motion.div>
            <motion.div className="trust-strip" variants={fadeUp}>
              <div className="trust-logos">
                {PLATFORMS.map((p) => (
                  <span key={p} className={`pf pf-${p}`}>
                    <PlatformLogo platform={p} />
                  </span>
                ))}
              </div>
              <span className="t-caption" style={{ textTransform: "none", letterSpacing: 0 }}>
                Connect all your accounts in minutes.
              </span>
            </motion.div>
          </motion.div>

          <motion.div
            className="hero-demo-wrap"
            style={{ position: "relative" }}
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1], delay: 0.15 }}
          >
            <div className="sticky-peek" />
            <HeroDemo />
          </motion.div>
        </div>
      </header>

      {/* ===== Social proof ===== */}
      {logos.length > 0 && (
        <section className="lp-section proof" style={{ padding: "48px 32px" }}>
          <div className="proof-label t-body-s">Trusted by teams who post everywhere</div>
          <div className="proof-row">
            {logos.map((l) => (
              <span key={l} className="proof-logo">
                {l}
              </span>
            ))}
          </div>
        </section>
      )}

      {/* ===== How it works ===== */}
      <section className="lp-section lp-rhythm" id="how">
        <motion.div className="how-head" {...revealOnView} variants={fadeUp}>
          <div className="section-eyebrow" style={{ marginBottom: 14 }}>
            How it works
          </div>
          <h2 className="t-h1">From one idea to everywhere, in three steps.</h2>
        </motion.div>
        <motion.div className="steps" {...revealOnView} variants={staggerContainer(0.12)}>
          {[
            { n: "01", v: "compose", t: "Write your idea", d: "Drop one post into a single clean composer." },
            { n: "02", v: "ai", t: "AI makes it native", d: "Postit rewrites tone, length, hashtags and format for each platform." },
            { n: "03", v: "calendar", t: "Publish or schedule", d: "Post once — it goes live everywhere, or queues for the perfect time." },
          ].map((s) => (
            <motion.div key={s.n} className="step-card" variants={fadeUp}>
              <div className="step-num">{s.n}</div>
              <div
                className="step-illus"
                style={{ height: "auto", padding: 0, background: "none", marginBottom: 20 }}
              >
                <ProductMock variant={s.v as "compose"} />
              </div>
              <h3 className="t-h3">{s.t}</h3>
              <p>{s.d}</p>
            </motion.div>
          ))}
        </motion.div>
      </section>

      {/* ===== Feature deep-dives (from site content) ===== */}
      <section className="lp-section lp-rhythm" id="features">
        {features.map((f, i) => (
          <motion.div
            key={i}
            className={"feat-row" + (i % 2 === 1 ? " reverse" : "")}
            {...revealOnView}
            variants={staggerContainer(0.1)}
          >
            <motion.div className="feat-text" variants={fadeUp}>
              <span className="badge badge-spark">
                <span className="badge-dot" /> {featureMeta(f.icon).tag}
              </span>
              <h3>{f.title}</h3>
              <p>{f.body}</p>
            </motion.div>
            <motion.div
              className="feat-shot"
              style={{ height: "auto", padding: 0, background: "none", border: "none", boxShadow: "none" }}
              variants={fadeUp}
            >
              <ProductMock variant={featureMeta(f.icon).variant} />
            </motion.div>
          </motion.div>
        ))}
      </section>

      {/* ===== Stats band ===== */}
      <section className="lp-section" style={{ padding: "48px 32px" }}>
        <motion.div className="stats-band" {...revealOnView} variants={fadeUp}>
          <div className="stats-grid">
            <div>
              <div className="stat-num">9×</div>
              <div className="stat-label">fewer copy-pastes</div>
            </div>
            <div>
              <div className="stat-num">Minutes</div>
              <div className="stat-label">not mornings</div>
            </div>
            <div>
              <div className="stat-num">1</div>
              <div className="stat-label">composer to rule them all</div>
            </div>
          </div>
        </motion.div>
      </section>

      {/* ===== Testimonials ===== */}
      {testimonials.length > 0 && (
        <section className="lp-section lp-rhythm">
          <motion.div className="tst-head" {...revealOnView} variants={fadeUp}>
            <div className="section-eyebrow" style={{ marginBottom: 14 }}>
              Loved by busy people
            </div>
            <h2 className="t-h1">The morning copy-paste ritual is over.</h2>
          </motion.div>
          <motion.div className="tst-grid" {...revealOnView} variants={staggerContainer(0.1)}>
            {testimonials.map((t, i) => (
              <motion.div key={i} className="tst-card" variants={fadeUp}>
                <p className="tst-quote">“{t.quote}”</p>
                <div className="tst-who">
                  <div className="tst-avatar">
                    {t.name.split(" ").map((p) => p[0]).slice(0, 2).join("")}
                  </div>
                  <div>
                    <div className="tst-name">{t.name}</div>
                    <div className="tst-role">{t.role}</div>
                  </div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </section>
      )}

      {/* ===== Pricing ===== */}
      {showPricing && <PricingTable />}

      {/* ===== FAQ ===== */}
      {faq.length > 0 && (
        <section className="lp-section lp-rhythm">
          <motion.div className="how-head" {...revealOnView} variants={fadeUp}>
            <div className="section-eyebrow" style={{ marginBottom: 14 }}>
              Questions
            </div>
            <h2 className="t-h1">Everything you might be wondering.</h2>
          </motion.div>
          <div className="lp-faq">
            {faq.map((item, i) => (
              <div key={i} className={"lp-faq-item" + (openFaq === i ? " open" : "")}>
                <button className="lp-faq-q" onClick={() => setOpenFaq(openFaq === i ? null : i)}>
                  {item.q}
                  <span className="chev">
                    <Icon name="chevd" size={18} />
                  </span>
                </button>
                {openFaq === i && <div className="lp-faq-a">{item.a}</div>}
              </div>
            ))}
          </div>
        </section>
      )}

      {/* ===== Final CTA ===== */}
      <section className="lp-section">
        <motion.div className="final-cta" {...revealOnView} variants={fadeUp}>
          <div className="sticky-peek" />
          <div className="sticky-peek two" />
          <h2 className="t-display-l">Your next post is already nine posts.</h2>
          <p className="sub">Write the idea once. Let Postit make it native everywhere.</p>
          <Link href="/signup" className="btn btn-spark btn-lg">
            Start free
          </Link>
          <p className="reassure t-body-s">Free forever plan · No credit card · Connect in minutes.</p>
        </motion.div>
      </section>

      {/* ===== Footer ===== */}
      <footer className="footer">
        <div className="footer-inner">
          <div className="footer-cols">
            <div className="footer-brand">
              <Link href="/" className="wordmark" style={{ fontSize: 22 }}>
                <span className="wm-text">Postit</span>
                <span className="wm-corner" />
              </Link>
              <p className="tagline">Write once. Post everywhere. Sound native on each.</p>
            </div>
            <div className="footer-col">
              <h4>Product</h4>
              <a href="#features">Features</a>
              <a href="#pricing">Pricing</a>
              <Link href="/app">Open app</Link>
            </div>
            <div className="footer-col">
              <h4>Platforms</h4>
              <a href="#how">How it works</a>
            </div>
            <div className="footer-col">
              <h4>Company</h4>
              <Link href="/login">Log in</Link>
              <Link href="/signup">Sign up</Link>
            </div>
          </div>
          <div className="footer-legal">
            <span>© {new Date().getFullYear()} Postit, Inc.</span>
            <span className="spacer" />
          </div>
        </div>
      </footer>
    </>
  );
}
