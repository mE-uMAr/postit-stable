"use client";

import { usePathname, useRouter } from "next/navigation";
import { Icon } from "@/components/Icon";
import { useAuth } from "@/components/auth/AuthProvider";
import { useTheme } from "./providers/ThemeProvider";

const TITLES: Record<string, string> = {
  compose: "Compose",
  calendar: "Calendar",
  posts: "Posts",
  connections: "Connections",
  analytics: "Analytics",
  settings: "Settings",
};

export function Topbar() {
  const pathname = usePathname();
  const router = useRouter();
  const { theme, toggle } = useTheme();
  const { user, logout } = useAuth();

  const segment = pathname.split("/").filter(Boolean).pop() ?? "compose";
  const title = TITLES[segment] ?? "Compose";
  const initials =
    (user?.full_name ?? "")
      .split(" ")
      .map((p) => p[0])
      .slice(0, 2)
      .join("")
      .toUpperCase() || "··";

  return (
    <header className="topbar">
      <h1>{title}</h1>
      <span className="spacer" />
      <div className="topbar-search">
        <Icon name="search" size={17} />
        <input placeholder="Search posts, platforms…" />
      </div>
      <button className="icon-btn" title="Toggle theme" onClick={toggle}>
        <Icon name={theme === "dark" ? "sun" : "moon"} size={19} />
      </button>
      <button className="icon-btn" title="Notifications">
        <Icon name="bell" size={19} />
        <span className="dot" />
      </button>
      <button className="btn btn-spark" onClick={() => router.push("/app/compose")}>
        <Icon name="plus" size={18} /> New post
      </button>
      <button className="avatar-btn" title="Sign out" onClick={() => void logout()}>
        {initials}
      </button>
    </header>
  );
}
