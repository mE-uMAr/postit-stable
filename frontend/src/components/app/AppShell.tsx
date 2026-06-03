"use client";

import { usePathname } from "next/navigation";
import { useState, type CSSProperties, type ReactNode } from "react";
import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";

export function AppShell({ children }: { children: ReactNode }) {
  const [collapsed, setCollapsed] = useState(false);
  const pathname = usePathname();
  const isCompose = pathname === "/app/compose";

  // Compose owns its own scrolling + an absolutely-positioned action bar.
  const viewStyle: CSSProperties | undefined = isCompose
    ? { overflow: "hidden", position: "relative" }
    : undefined;

  return (
    <div className="app-root">
      <Sidebar collapsed={collapsed} setCollapsed={setCollapsed} />
      <div className="main">
        <Topbar />
        <div className="view" style={viewStyle}>
          {children}
        </div>
      </div>
    </div>
  );
}
