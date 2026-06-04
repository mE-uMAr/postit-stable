"use client";

import { usePathname, useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { Icon } from "@/components/Icon";
import { useAuth } from "@/components/auth/AuthProvider";
import { useTheme } from "./providers/ThemeProvider";
import { api } from "@/lib/api/client";
import type { ApiPost, Paginated } from "@/lib/api/types";

const TITLES: Record<string, string> = {
  compose: "Compose",
  calendar: "Calendar",
  posts: "Posts",
  connections: "Connections",
  analytics: "Analytics",
  settings: "Settings",
};

interface Notif {
  id: string;
  title: string;
  body: string | null;
  read_at: string | null;
  created_at: string;
}

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

  // ---- Search ----
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<ApiPost[]>([]);
  const [searchOpen, setSearchOpen] = useState(false);
  const searchRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!query.trim()) {
      setResults([]);
      return;
    }
    const t = setTimeout(async () => {
      try {
        const res = await api.get<Paginated<ApiPost>>(
          `posts?size=6&q=${encodeURIComponent(query.trim())}`,
        );
        setResults(res.items);
        setSearchOpen(true);
      } catch {
        setResults([]);
      }
    }, 220);
    return () => clearTimeout(t);
  }, [query]);

  // ---- Notifications ----
  const [notifs, setNotifs] = useState<Notif[]>([]);
  const [notifOpen, setNotifOpen] = useState(false);
  const notifRef = useRef<HTMLDivElement>(null);
  const unread = notifs.filter((n) => !n.read_at).length;

  const loadNotifs = async () => {
    try {
      setNotifs(await api.get<Notif[]>("notifications"));
    } catch {
      /* ignore */
    }
  };
  useEffect(() => {
    void loadNotifs();
  }, []);

  // Close popovers on outside click.
  useEffect(() => {
    const onDoc = (e: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(e.target as Node)) setSearchOpen(false);
      if (notifRef.current && !notifRef.current.contains(e.target as Node)) setNotifOpen(false);
    };
    document.addEventListener("mousedown", onDoc);
    return () => document.removeEventListener("mousedown", onDoc);
  }, []);

  const openNotifs = async () => {
    const willOpen = !notifOpen;
    setNotifOpen(willOpen);
    if (willOpen) {
      await loadNotifs();
      // Mark the currently-unread items as read (best-effort).
      for (const n of notifs.filter((x) => !x.read_at)) {
        api.post(`notifications/${n.id}/read`).catch(() => {});
      }
      setTimeout(() => void loadNotifs(), 500);
    }
  };

  const gotoPosts = () => {
    setSearchOpen(false);
    setQuery("");
    router.push("/app/posts");
  };

  return (
    <header className="topbar">
      <h1>{title}</h1>
      <span className="spacer" />

      <div className="topbar-search tb-pop-wrap" ref={searchRef}>
        <Icon name="search" size={17} />
        <input
          placeholder="Search posts…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => results.length && setSearchOpen(true)}
          onKeyDown={(e) => e.key === "Enter" && gotoPosts()}
        />
        {searchOpen && query.trim() && (
          <div className="tb-pop tb-search-results">
            {results.length === 0 ? (
              <div className="tb-pop-empty">No posts match “{query.trim()}”.</div>
            ) : (
              results.map((p) => (
                <div key={p.id} className="tb-pop-item" onClick={gotoPosts}>
                  <div>
                    <div className="t">{p.title}</div>
                    <div className="b">{p.status}</div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>

      <button className="icon-btn" title="Toggle theme" onClick={toggle}>
        <Icon name={theme === "dark" ? "sun" : "moon"} size={19} />
      </button>

      <div className="tb-pop-wrap" ref={notifRef}>
        <button className="icon-btn" title="Notifications" onClick={() => void openNotifs()}>
          <Icon name="bell" size={19} />
          {unread > 0 && <span className="dot" />}
        </button>
        {notifOpen && (
          <div className="tb-pop">
            <div className="tb-pop-head">
              <span>Notifications</span>
              {unread > 0 && <span className="role-badge">{unread} new</span>}
            </div>
            {notifs.length === 0 ? (
              <div className="tb-pop-empty">You&apos;re all caught up. 🎉</div>
            ) : (
              notifs.slice(0, 12).map((n) => (
                <div key={n.id} className={"tb-pop-item" + (n.read_at ? " read" : "")}>
                  <span className="dot" />
                  <div>
                    <div className="t">{n.title}</div>
                    {n.body && <div className="b">{n.body}</div>}
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>

      <button className="btn btn-spark" onClick={() => router.push("/app/compose")}>
        <Icon name="plus" size={18} /> New post
      </button>
      <button className="avatar-btn" title="Sign out" onClick={() => void logout()}>
        {initials}
      </button>
    </header>
  );
}
