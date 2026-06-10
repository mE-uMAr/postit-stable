"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

export function LandingNav() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <nav className={"nav" + (scrolled ? " scrolled" : "")} id="nav">
      <div className="nav-inner">
        <Link href="/" className="wordmark" style={{ fontSize: 24 }}>
          <span className="wm-text">Postit</span>
          <span className="wm-corner" />
        </Link>
        <div className="nav-links">
          <Link href="/#features">Features</Link>
          <Link href="/#how">How it works</Link>
          <Link href="/pricing">Pricing</Link>
        </div>
        <div className="nav-right">
          <Link href="/login" className="btn btn-ghost btn-sm">
            Log in
          </Link>
          <Link href="/signup" className="btn btn-spark btn-sm">
            Start free
          </Link>
        </div>
      </div>
    </nav>
  );
}
