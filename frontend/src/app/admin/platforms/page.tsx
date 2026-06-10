"use client";

import { Icon } from "@/components/Icon";
import { PlatformLogo } from "@/components/PlatformLogo";
import { useToast } from "@/components/app/providers/ToastProvider";
import { useConfirm } from "@/components/app/providers/ConfirmProvider";
import { api } from "@/lib/api/client";
import { errorMessage, useApi } from "@/lib/api/useApi";
import type { ApiPlatform, IntegrationsResponse, PlatformIntegration, PlatformKey } from "@/lib/api/types";

export default function AdminPlatformsPage() {
  const pushToast = useToast();
  const confirm = useConfirm();
  const { data, loading, reload } = useApi<ApiPlatform[]>("admin/platforms");
  const integrations = useApi<IntegrationsResponse>("admin/integrations");
  const intByPlatform = new Map<string, PlatformIntegration>(
    (integrations.data?.platforms ?? []).map((p) => [p.platform_id, p]),
  );

  const copy = async (label: string, value: string) => {
    try {
      await navigator.clipboard.writeText(value);
      pushToast(`${label} copied`);
    } catch {
      pushToast("Couldn't copy to clipboard");
    }
  };

  const toggle = async (p: ApiPlatform) => {
    if (p.is_active) {
      const ok = await confirm({
        title: `Disable ${p.name} for everyone?`,
        body: (
          <>
            {p.name} will be hidden in the composer for <strong>all</strong> workspaces and new posts
            can&apos;t target it. Existing scheduled posts to {p.name} may fail to publish.
          </>
        ),
        confirmLabel: `Disable ${p.name}`,
        danger: true,
      });
      if (!ok) return;
    }
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
          <p>
            Enable or disable networks, and copy each network&apos;s OAuth callback URLs into its
            developer console.
          </p>
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
              <button className="btn btn-secondary btn-sm" onClick={() => void toggle(p)}>
                {p.is_active ? "Disable" : "Enable"}
              </button>
            </div>
            <CallbackUrls integ={intByPlatform.get(p.id)} onCopy={copy} />
          </div>
        ))}
      </div>
    </div>
  );
}

function CallbackUrls({
  integ,
  onCopy,
}: {
  integ?: PlatformIntegration;
  onCopy: (label: string, value: string) => void;
}) {
  if (!integ) return null;
  const rows: { label: string; value: string }[] = [
    { label: "Redirect callback", value: integ.redirect_callback_url },
    { label: "Deauthorize callback", value: integ.deauthorize_callback_url },
    { label: "Delete callback", value: integ.delete_callback_url },
  ];
  return (
    <div className="cb-block">
      <span className={"cb-status " + (integ.configured ? "on" : "off")}>
        <span className="badge-dot" />
        {integ.configured ? "Credentials set" : "No credentials yet"}
      </span>
      {rows.map((r) => (
        <div key={r.label} className="cb-row">
          <span className="cb-label">{r.label}</span>
          <button className="cb-copy" title="Copy" onClick={() => onCopy(r.label, r.value)}>
            <code>{r.value}</code>
            <span className="cb-ic">
              <Icon name="duplicate" size={14} />
            </span>
          </button>
        </div>
      ))}
    </div>
  );
}
