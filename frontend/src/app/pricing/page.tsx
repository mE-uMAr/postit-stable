"use client";

import Link from "next/link";

import { LandingIconSprite } from "@/components/landing/LandingIconSprite";
import { LandingNav } from "@/components/landing/LandingNav";
import { LandingFooter } from "@/components/landing/LandingFooter";
import { PricingContent } from "@/components/landing/PricingContent";
import { useApi } from "@/lib/api/useApi";
import type { SiteContent } from "@/lib/api/types";

import "@/styles/landing.css";

export default function PricingPage() {
  const { data, loading } = useApi<SiteContent>("site/content");
  const show = data?.flags?.show_pricing ?? true;

  return (
    <>
      <LandingIconSprite />
      <LandingNav />

      <main style={{ paddingTop: 72 }}>
        {loading ? (
          <div className="lp-section lp-rhythm" style={{ textAlign: "center", color: "var(--ink-faint)" }}>
            Loading pricing…
          </div>
        ) : show ? (
          <PricingContent />
        ) : (
          <section className="lp-section lp-rhythm" style={{ textAlign: "center" }}>
            <h1 className="t-h1">Pricing is coming soon</h1>
            <p className="t-body-l" style={{ color: "var(--ink-soft)", margin: "16px auto 28px", maxWidth: 520 }}>
              We&apos;re finalising plans. In the meantime you can start free and explore everything Postit does.
            </p>
            <Link href="/signup" className="btn btn-spark btn-lg">
              Start free
            </Link>
          </section>
        )}
      </main>

      <LandingFooter />
    </>
  );
}
