"use client";

import { PlatformLogo } from "@/components/PlatformLogo";
import { useToast } from "@/components/app/providers/ToastProvider";
import { api } from "@/lib/api/client";
import { errorMessage, useApi } from "@/lib/api/useApi";
import type { ApiPlatform, PlatformKey } from "@/lib/api/types";

export default function AdminPlatformsPage() {
  const pushToast = useToast();
  const { data, loading, reload } = useApi<ApiPlatform[]>("admin/platforms");

  const toggle = async (p: ApiPlatform) => {
    try {
      await api.patch(`admin/platforms/${p.id}`, { is_active: !p.is_active });
      await reload();
      pushToast(`${p.name} ${p.is_active ? "disabled" : "enabled"}`);
    } catch (e) {
      pushToast(errorMessage(e));
    }
  };

  return (
    <div className="view-pad">
      <div className="vh">
        <div className="vh-title">
          <h2>Platforms</h2>
          <p>Enable or disable networks across the whole product.</p>
        </div>
      </div>

      {loading && <div className="post-sub">Loading…</div>}

      <div className="conn-grid">
        {(data ?? []).map((p) => (
          <div key={p.id} className="conn-card">
            <div className="conn-top">
              <span className={"pf pf-" + p.id}>
                <PlatformLogo platform={p.id as PlatformKey} />
              </span>
              <div>
                <div className="conn-name">{p.name}</div>
                <span className="post-sub">
                  {p.char_limit ? `${p.char_limit} chars` : "no limit"}
                  {p.requires_video ? " · video" : p.requires_media ? " · media" : ""}
                </span>
              </div>
            </div>
            <div className="conn-foot">
              <span className={"badge " + (p.is_active ? "badge-success" : "")} style={!p.is_active ? { background: "var(--surface-sunken)", color: "var(--ink-faint)" } : undefined}>
                <span className="badge-dot" /> {p.is_active ? "Active" : "Disabled"}
              </span>
              <button className="btn btn-secondary btn-sm" onClick={() => toggle(p)}>
                {p.is_active ? "Disable" : "Enable"}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
