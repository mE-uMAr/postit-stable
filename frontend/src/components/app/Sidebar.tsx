"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Icon } from "@/components/Icon";
import { Wordmark } from "@/components/Wordmark";
import { useAuth } from "@/components/auth/AuthProvider";
import type { IconName } from "@/lib/icons";

interface NavItem {
  key: string;
  label: string;
  icon: IconName;
  href: string;
}

const NAV: NavItem[] = [
  { key: "compose", label: "Compose", icon: "compose", href: "/app/compose" },
  { key: "calendar", label: "Calendar", icon: "calendar", href: "/app/calendar" },
  { key: "posts", label: "Posts", icon: "posts", href: "/app/posts" },
  { key: "connections", label: "Connections", icon: "connections", href: "/app/connections" },
  { key: "analytics", label: "Analytics", icon: "analytics", href: "/app/analytics" },
  { key: "settings", label: "Settings", icon: "settings", href: "/app/settings" },
];

interface SidebarProps {
  collapsed: boolean;
  setCollapsed: (updater: (c: boolean) => boolean) => void;
}

export function Sidebar({ collapsed, setCollapsed }: SidebarProps) {
  const pathname = usePathname();
  const { user } = useAuth();
  const isActive = (href: string) => pathname === href || pathname.startsWith(href + "/");

  return (
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
        <Link
          href="/app/compose"
          className={"sb-item sb-compose" + (isActive("/app/compose") ? " active" : "")}
          title="Compose"
        >
          <span className="sb-ico">
            <Icon name="compose" size={21} />
          </span>
          <span className="sb-label">Compose</span>
        </Link>
        {NAV.slice(1).map((n) => (
          <Link
            key={n.key}
            href={n.href}
            className={"sb-item" + (isActive(n.href) ? " active" : "")}
            title={n.label}
          >
            <span className="sb-ico">
              <Icon name={n.icon} size={21} />
            </span>
            <span className="sb-label">{n.label}</span>
          </Link>
        ))}
        {user?.is_superuser && (
          <Link href="/admin" className="sb-item" title="Admin">
            <span className="sb-ico">
              <Icon name="shield" size={21} />
            </span>
            <span className="sb-label">Admin</span>
          </Link>
        )}
      </nav>
      <div className="sb-foot">
        <div className="sb-ws">
          <div className="sb-ws-logo">M</div>
          <div className="sb-ws-meta">
            <div className="sb-ws-name">Maple &amp; Co</div>
            <div className="sb-ws-plan">Pro plan</div>
          </div>
          <span className="chev" style={{ marginLeft: "auto", color: "var(--ink-faint)" }}>
            <Icon name="chevd" size={16} />
          </span>
        </div>
      </div>
    </aside>
  );
}
