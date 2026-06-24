"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { api } from "@/lib/api/client";
import type { ApiUser } from "@/lib/api/types";

export function LandingNav() {
  const [scrolled, setScrolled] = useState(false);
  const [user, setUser] = useState<ApiUser | null>(null);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  // The session cookies are httpOnly, so the browser can't read them directly.
  // Ask the backend (via the same-origin proxy, which attaches the token) who we
  // are, so the nav reflects the logged-in state instead of always showing "Log in".
  useEffect(() => {
    let active = true;
    api
      .get<ApiUser>("auth/me")
      .then((u) => active && setUser(u))
      .catch(() => active && setUser(null)); // 401 → treat as guest
    return () => {
      active = false;
    };
  }, []);

  // Superusers live in the admin console; everyone else uses the workspace app
  // (mirrors the middleware redirects).
  const dashboardHref = user?.is_superuser ? "/admin" : "/app";

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
          {user ? (
            <Link href={dashboardHref} className="btn btn-spark btn-sm">
              Dashboard
            </Link>
          ) : (
            <>
              <Link href="/login" className="btn btn-ghost btn-sm">
                Log in
              </Link>
              <Link href="/signup" className="btn btn-spark btn-sm">
                Start free
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
