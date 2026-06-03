"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, type ReactNode } from "react";

import { Icon } from "@/components/Icon";
import { Wordmark } from "@/components/Wordmark";
import { useAuth } from "@/components/auth/AuthProvider";
import { useTheme } from "@/components/app/providers/ThemeProvider";
import type { IconName } from "@/lib/icons";

interface NavItem {
  label: string;
  icon: IconName;
  href: string;
}

const NAV: NavItem[] = [
  { label: "Dashboard", icon: "analytics", href: "/admin" },
  { label: "Users", icon: "user", href: "/admin/users" },
  { label: "Subscriptions", icon: "card", href: "/admin/subscriptions" },
  { label: "Plans", icon: "duplicate", href: "/admin/plans" },
  { label: "Platforms", icon: "connections", href: "/admin/platforms" },
  { label: "Audit log", icon: "posts", href: "/admin/audit" },
];

const TITLES: Record<string, string> = {
  "/admin": "Dashboard",
  "/admin/users": "Users",
  "/admin/subscriptions": "Subscriptions",
  "/admin/plans": "Plans",
  "/admin/platforms": "Platforms",
  "/admin/audit": "Audit log",
};

export function AdminShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const { theme, toggle } = useTheme();
  const { user, logout } = useAuth();
  const [collapsed, setCollapsed] = useState(false);

  const isActive = (href: string) => (href === "/admin" ? pathname === "/admin" : pathname.startsWith(href));
  const title = TITLES[pathname] ?? "Admin";
  const initials =
    (user?.full_name ?? "")
      .split(" ")
      .map((p) => p[0])
      .slice(0, 2)
      .join("")
      .toUpperCase() || "AD";

  return (
    <div className="app-root">
      <aside className={"sidebar" + (collapsed ? " collapsed" : "")}>
        <div className="sb-top">
          {!collapsed && (
            <Link href="/">
              <Wordmark size={24} />
            </Link>
          )}
          <button className="sb-collapse" onClick={() => setCollapsed((c) => !c)} title="Collapse">
            <Icon name="panel" size={18} />
          </button>
        </div>
        <nav className="sb-nav">
          {NAV.map((n) => (
            <Link key={n.href} href={n.href} className={"sb-item" + (isActive(n.href) ? " active" : "")} title={n.label}>
              <span className="sb-ico">
                <Icon name={n.icon} size={21} />
              </span>
              <span className="sb-label">{n.label}</span>
            </Link>
          ))}
        </nav>
        <div className="sb-foot">
          <div className="sb-ws">
            <div className="sb-ws-logo" style={{ background: "var(--ai)" }}>
              A
            </div>
            <div className="sb-ws-meta">
              <div className="sb-ws-name">Admin console</div>
              <div className="sb-ws-plan">Superuser</div>
            </div>
          </div>
        </div>
      </aside>

      <div className="main">
        <header className="topbar">
          <h1>{title}</h1>
          <span className="spacer" />
          <Link href="/app/compose" className="btn btn-ghost btn-sm">
            ← Back to app
          </Link>
          <button className="icon-btn" title="Toggle theme" onClick={toggle}>
            <Icon name={theme === "dark" ? "sun" : "moon"} size={19} />
          </button>
          <button className="avatar-btn" title="Sign out" onClick={() => void logout()}>
            {initials}
          </button>
        </header>
        <div className="view">{children}</div>
      </div>
    </div>
  );
}
