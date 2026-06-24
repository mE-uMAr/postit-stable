"use client";

import { useEffect, useMemo, useState } from "react";
import { Icon } from "@/components/Icon";
import { PlatformLogo } from "@/components/PlatformLogo";
import { api } from "@/lib/api/client";
import { errorMessage, useApi } from "@/lib/api/useApi";
import type { ApiConnection, ApiPlatform, ConnectionStatus, PlatformKey } from "@/lib/api/types";
import { useToast } from "./providers/ToastProvider";
import { useConfirm } from "./providers/ConfirmProvider";

function StatusBadge({ status }: { status: ConnectionStatus }) {
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
  const confirm = useConfirm();
  const platforms = useApi<ApiPlatform[]>("platforms");
  const connections = useApi<ApiConnection[]>("connections");
  const [busy, setBusy] = useState<string | null>(null);

  const byPlatform = useMemo(() => {
    const map = new Map<string, ApiConnection>();
    (connections.data ?? []).forEach((c) => map.set(c.platform_id, c));
    return map;
  }, [connections.data]);

  const connectedCount = (connections.data ?? []).filter((c) => c.status === "connected").length;
  const totalCount = (platforms.data ?? []).length;

  // Surface the result of an OAuth round-trip (callback redirects back here).
  useEffect(() => {
    const sp = new URLSearchParams(window.location.search);
    const connected = sp.get("connected");
    const err = sp.get("error");
    const platform = sp.get("platform") ?? "Account";
    if (!connected && !err) return;
    if (connected) pushToast(`${platform} connected`);
    else pushToast(`Couldn't connect ${platform}: ${err}`);
    window.history.replaceState({}, "", "/app/connections");
    void connections.reload();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const act = async (platformId: string, action: "connect" | "disconnect" | "reconnect", name: string) => {
    if (action === "disconnect") {
      const ok = await confirm({
        title: `Disconnect ${name}?`,
        body: (
          <>
            Postit will stop posting to <strong>{name}</strong> and any scheduled posts targeting it
            won&apos;t go out. You can reconnect any time.
          </>
        ),
        confirmLabel: "Disconnect",
        danger: true,
      });
      if (!ok) return;
      setBusy(platformId + action);
      try {
        await api.post(`connections/${platformId}/disconnect`, {});
        await connections.reload();
        pushToast(`${name} disconnected`);
      } catch (e) {
        pushToast(errorMessage(e));
      } finally {
        setBusy(null);
      }
      return;
    }
    // connect / reconnect → start real OAuth: fetch the consent URL and go there.
    setBusy(platformId + action);
    try {
      const { authorize_url } = await api.post<{ authorize_url: string }>(
        `connections/${platformId}/${action}`,
      );
      window.location.href = authorize_url;
    } catch (e) {
      pushToast(errorMessage(e));
      setBusy(null);
    }
  };

  const loading = platforms.loading || connections.loading;
  const error = platforms.error || connections.error;

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
      </div>

      {loading && <div className="post-sub">Loading connections…</div>}
      {error && <div className="conn-banner" style={{ background: "var(--danger-tint)" }}>{error}</div>}

      {!loading && !error && (
        <>
          <div className="conn-banner">
            <span className="ic">
              <Icon name="shield" size={20} />
            </span>
            <span>
              <strong>
                {connectedCount} of {totalCount} platforms connected.
              </strong>{" "}
              Reconnect any expired accounts to keep posts flowing.
            </span>
          </div>

          <div className="conn-grid">
            {(platforms.data ?? []).map((p) => {
              const conn = byPlatform.get(p.id);
              const status: ConnectionStatus = conn?.status ?? "disconnected";
              return (
                <div key={p.id} className="conn-card">
                  <div className="conn-top">
                    <span className={"pf pf-" + p.id}>
                      <PlatformLogo platform={p.id as PlatformKey} />
                    </span>
                    <div>
                      <div className="conn-name">{p.name}</div>
                      <StatusBadge status={status} />
                    </div>
                  </div>
                  {conn?.handle ? (
                    <div className="conn-acct">
                      <span className="av">{conn.avatar_text ?? p.name[0]}</span>
                      <span className="handle">{conn.handle}</span>
                    </div>
                  ) : (
                    <div className="conn-acct">
                      <span className="handle ink-faint">No account linked yet.</span>
                    </div>
                  )}
                  <div className="conn-foot">
                    {status === "connected" && (
                      <button
                        className="btn btn-ghost btn-sm"
                        style={{ color: "var(--ink-faint)" }}
                        disabled={busy !== null}
                        onClick={() => act(p.id, "disconnect", p.name)}
                      >
                        Disconnect
                      </button>
                    )}
                    {status === "expired" && (
                      <>
                        <span className="post-sub">Token expired</span>
                        <button
                          className="btn btn-spark btn-sm"
                          disabled={busy !== null}
                          onClick={() => act(p.id, "reconnect", p.name)}
                        >
                          <Icon name="refresh" size={15} /> Reconnect
                        </button>
                      </>
                    )}
                    {(status === "disconnected" || status === "revoked") && (
                      <>
                        <span className="spacer" />
                        <button
                          className="btn btn-secondary btn-sm"
                          disabled={busy !== null}
                          onClick={() => act(p.id, "connect", p.name)}
                        >
                          Connect
                        </button>
                      </>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}
