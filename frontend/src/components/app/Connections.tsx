"use client";

import { useState } from "react";
import { Icon } from "@/components/Icon";
import { PlatformLogo } from "@/components/PlatformLogo";
import { PF } from "@/lib/platforms";
import type { PlatformKey } from "@/lib/types";
import { useToast } from "./providers/ToastProvider";

type ConnStatus = "connected" | "expired" | "disconnected";

interface Conn {
  key: PlatformKey;
  status: ConnStatus;
  handle: string | null;
  av: string | null;
}

const CONNS: Conn[] = [
  { key: "x", status: "connected", handle: "@maplehome", av: "M" },
  { key: "linkedin", status: "connected", handle: "Maple & Co", av: "M" },
  { key: "instagram", status: "connected", handle: "maple.home", av: "m" },
  { key: "threads", status: "connected", handle: "maple.home", av: "m" },
  { key: "facebook", status: "connected", handle: "Maple & Co Home", av: "M" },
  { key: "youtube", status: "expired", handle: "Maple & Co", av: "M" },
  { key: "tiktok", status: "disconnected", handle: null, av: null },
  { key: "wordpress", status: "connected", handle: "maple.blog", av: "W" },
  { key: "blogger", status: "disconnected", handle: null, av: null },
];

function StatusBadge({ status }: { status: ConnStatus }) {
  if (status === "connected")
    return (
      <span className="badge badge-success">
        <span className="badge-dot" /> Connected
      </span>
    );
  if (status === "expired")
    return (
      <span className="badge badge-warning">
        <span className="badge-dot" /> Expired
      </span>
    );
  return (
    <span className="badge" style={{ background: "var(--surface-sunken)", color: "var(--ink-faint)" }}>
      <span className="badge-dot" /> Not connected
    </span>
  );
}

export function Connections() {
  const pushToast = useToast();
  const [conns, setConns] = useState<Conn[]>(CONNS);

  const act = (key: PlatformKey, to: ConnStatus) => {
    setConns((cs) =>
      cs.map((c) =>
        c.key === key
          ? { ...c, status: to, handle: to === "disconnected" ? null : c.handle || PF[key].author }
          : c,
      ),
    );
    pushToast(
      to === "connected"
        ? `${PF[key].name} connected`
        : to === "disconnected"
          ? `${PF[key].name} disconnected`
          : `${PF[key].name} reconnected`,
    );
  };

  return (
    <div className="view-pad">
      <div className="vh">
        <div className="vh-title">
          <h2>Connections</h2>
          <p>
            Postit connects through secure OAuth. We never store your passwords, and you control exactly what
            posts where.
          </p>
        </div>
        <div className="vh-actions">
          <button className="btn btn-secondary">
            <Icon name="plus" size={17} /> Connect account
          </button>
        </div>
      </div>

      <div className="conn-banner">
        <span className="ic">
          <Icon name="shield" size={20} />
        </span>
        <span>
          <strong>7 of 9 platforms connected.</strong> Reconnect YouTube to keep video posts flowing — its
          access token expired.
        </span>
      </div>

      <div className="conn-grid">
        {conns.map((c) => {
          const p = PF[c.key];
          return (
            <div key={c.key} className="conn-card">
              <div className="conn-top">
                <span className={"pf " + p.cls}>
                  <PlatformLogo platform={p.key} />
                </span>
                <div>
                  <div className="conn-name">{p.name}</div>
                  <StatusBadge status={c.status} />
                </div>
              </div>
              {c.handle ? (
                <div className="conn-acct">
                  <span className="av">{c.av}</span>
                  <span className="handle">{c.handle}</span>
                </div>
              ) : (
                <div className="conn-acct">
                  <span className="handle ink-faint">No account linked yet.</span>
                </div>
              )}
              <div className="conn-foot">
                {c.status === "connected" && (
                  <>
                    <button className="btn btn-ghost btn-sm" onClick={() => act(c.key, "connected")}>
                      + Add account
                    </button>
                    <button
                      className="btn btn-ghost btn-sm"
                      style={{ color: "var(--ink-faint)" }}
                      onClick={() => act(c.key, "disconnected")}
                    >
                      Disconnect
                    </button>
                  </>
                )}
                {c.status === "expired" && (
                  <>
                    <span className="post-sub">Token expired 2d ago</span>
                    <button className="btn btn-spark btn-sm" onClick={() => act(c.key, "connected")}>
                      <Icon name="refresh" size={15} /> Reconnect
                    </button>
                  </>
                )}
                {c.status === "disconnected" && (
                  <>
                    <span className="spacer" />
                    <button className="btn btn-secondary btn-sm" onClick={() => act(c.key, "connected")}>
                      Connect
                    </button>
                  </>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
