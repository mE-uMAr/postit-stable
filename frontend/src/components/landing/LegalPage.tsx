import type { ReactNode } from "react";

import { LandingNav } from "@/components/landing/LandingNav";
import { LandingFooter } from "@/components/landing/LandingFooter";

import "@/styles/landing.css";

export function LegalPage({
  title,
  updated,
  children,
}: {
  title: string;
  updated: string;
  children: ReactNode;
}) {
  return (
    <>
      <LandingNav />
      <main className="legal-wrap">
        <h1>{title}</h1>
        <div className="legal-updated">Last updated: {updated}</div>
        <div className="legal-body">{children}</div>
      </main>
      <LandingFooter />
    </>
  );
}
