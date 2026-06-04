"use client";

import { useEffect, useState } from "react";
import { Icon } from "@/components/Icon";
import { Sparkle } from "@/components/Sparkle";
import { api, ApiError } from "@/lib/api/client";
import { errorMessage, useApi } from "@/lib/api/useApi";
import { openPaddleCheckout } from "@/lib/paddle";
import { useAuth } from "@/components/auth/AuthProvider";
import type {
  ApiBrandVoice,
  ApiMember,
  ApiNotificationPrefs,
  ApiPlan,
  ApiSubscription,
  ApiUsage,
  PaddleCheckout,
} from "@/lib/api/types";
import { useTheme } from "./providers/ThemeProvider";
import { useToast } from "./providers/ToastProvider";

const S_TABS = ["Profile", "Workspace & team", "Brand voice", "Billing", "Notifications"];

function Toggle({ on, onClick }: { on: boolean; onClick: () => void }) {
  return <button className={"switch" + (on ? " on" : "")} onClick={onClick} />;
}

function dollars(cents: number): string {
  return "$" + (cents / 100).toFixed(cents % 100 === 0 ? 0 : 2);
}

export function Settings() {
  const { theme, toggle } = useTheme();
  const pushToast = useToast();
  const { user, refresh } = useAuth();

  const [tab, setTab] = useState("Profile");

  return (
    <div className="view-pad">
      <div className="vh">
        <div className="vh-title">
          <h2>Settings</h2>
          <p>Manage your account, team, brand voice, and billing.</p>
        </div>
      </div>

      <div className="settings-layout">
        <div className="settings-tabs">
          {S_TABS.map((t) => (
            <button key={t} className={"settings-tab" + (tab === t ? " on" : "")} onClick={() => setTab(t)}>
              {t}
            </button>
          ))}
        </div>

        {tab === "Profile" && (
          <ProfilePanel
            name={user?.full_name ?? ""}
            email={user?.email ?? ""}
            avatar={(user?.full_name ?? "U").split(" ").map((p) => p[0]).slice(0, 2).join("").toUpperCase()}
            dark={theme === "dark"}
            onToggleDark={toggle}
            onSaved={refresh}
            pushToast={pushToast}
          />
        )}
        {tab === "Workspace & team" && <TeamPanel pushToast={pushToast} />}
        {tab === "Brand voice" && <BrandVoicePanel pushToast={pushToast} />}
        {tab === "Billing" && <BillingPanel pushToast={pushToast} />}
        {tab === "Notifications" && <NotificationsPanel pushToast={pushToast} />}
      </div>
    </div>
  );
}

/* --------------------------------- Profile -------------------------------- */
function ProfilePanel({
  name,
  email,
  avatar,
  dark,
  onToggleDark,
  onSaved,
  pushToast,
}: {
  name: string;
  email: string;
  avatar: string;
  dark: boolean;
  onToggleDark: () => void;
  onSaved: () => Promise<void>;
  pushToast: (m: string) => void;
}) {
  const [fullName, setFullName] = useState(name);
  useEffect(() => setFullName(name), [name]);

  const save = async () => {
    try {
      await api.patch("users/me", { full_name: fullName });
      await onSaved();
      pushToast("Profile saved");
    } catch (e) {
      pushToast(errorMessage(e));
    }
  };

  return (
    <div className="settings-panel">
      <h3>Profile</h3>
      <p className="desc">This is how you appear inside Postit.</p>
      <div style={{ display: "flex", alignItems: "center", gap: 18, marginBottom: 24 }}>
        <div className="avatar-lg">{avatar}</div>
        <button className="btn btn-secondary btn-sm"><Icon name="upload" size={16} /> Change photo</button>
      </div>
      <div className="settings-field field">
        <label className="field-label">Full name</label>
        <input className="input" value={fullName} onChange={(e) => setFullName(e.target.value)} />
      </div>
      <div className="settings-field field">
        <label className="field-label">Email</label>
        <input className="input" value={email} disabled />
      </div>
      <div className="settings-row">
        <div>
          <div className="lbl">Dark mode</div>
          <div className="sub">Use the dark theme across the app.</div>
        </div>
        <Toggle on={dark} onClick={onToggleDark} />
      </div>
      <button className="btn btn-spark" style={{ marginTop: 20 }} onClick={save}>Save changes</button>
    </div>
  );
}

/* ----------------------------------- Team --------------------------------- */
function TeamPanel({ pushToast }: { pushToast: (m: string) => void }) {
  const { data, loading, error, reload } = useApi<ApiMember[]>("members");
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("editor");

  const invite = async () => {
    if (!email.trim()) return;
    try {
      await api.post("members", { email: email.trim(), role });
      setEmail("");
      await reload();
      pushToast("Invitation sent");
    } catch (e) {
      pushToast(errorMessage(e));
    }
  };

  const remove = async (id: string) => {
    try {
      await api.del(`members/${id}`);
      await reload();
      pushToast("Member removed");
    } catch (e) {
      pushToast(errorMessage(e));
    }
  };

  return (
    <div className="settings-panel">
      <h3>Workspace &amp; team</h3>
      <p className="desc">Invite teammates and manage their roles.</p>
      {loading && <div className="post-sub">Loading…</div>}
      {error && <div className="post-sub">{error}</div>}
      {(data ?? []).map((m) => (
        <div key={m.id} className="team-row">
          <span className="av">{m.avatar}</span>
          <div style={{ flex: 1 }}>
            <div className="lbl" style={{ fontSize: 14 }}>{m.name}</div>
            <div className="sub">{m.email}</div>
          </div>
          <span className="pill">{m.role}</span>
          {m.role !== "owner" && (
            <button className="btn btn-ghost btn-sm" style={{ color: "var(--ink-faint)" }} onClick={() => remove(m.id)}>
              Remove
            </button>
          )}
        </div>
      ))}
      <div style={{ display: "flex", gap: 10, marginTop: 20 }}>
        <input
          className="input"
          placeholder="teammate@company.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <select className="input" style={{ maxWidth: 130 }} value={role} onChange={(e) => setRole(e.target.value)}>
          <option value="admin">Admin</option>
          <option value="editor">Editor</option>
          <option value="viewer">Viewer</option>
        </select>
        <button className="btn btn-secondary" onClick={invite}><Icon name="plus" size={16} /> Invite</button>
      </div>
    </div>
  );
}

/* -------------------------------- Brand voice ----------------------------- */
function BrandVoicePanel({ pushToast }: { pushToast: (m: string) => void }) {
  const { data, loading } = useApi<ApiBrandVoice>("brand-voice");
  const [tone, setTone] = useState("Match my brand");
  const [guidelines, setGuidelines] = useState("");
  const [avoid, setAvoid] = useState("");

  useEffect(() => {
    if (data) {
      setTone(data.tone);
      setGuidelines(data.guidelines ?? "");
      setAvoid((data.words_to_avoid ?? []).join(", "));
    }
  }, [data]);

  const save = async () => {
    try {
      await api.put("brand-voice", {
        tone,
        guidelines,
        words_to_avoid: avoid.split(",").map((w) => w.trim()).filter(Boolean),
      });
      pushToast("Brand voice updated");
    } catch (e) {
      pushToast(errorMessage(e));
    }
  };

  if (loading) return <div className="settings-panel"><div className="post-sub">Loading…</div></div>;

  return (
    <div className="settings-panel">
      <h3>Brand voice</h3>
      <p className="desc">The default tone Postit&apos;s AI uses when rewriting your posts.</p>
      <div className="tone-row" style={{ marginTop: 0, marginBottom: 20 }}>
        {["Professional", "Casual", "Bold", "Match my brand"].map((t) => (
          <button key={t} className={"tone-chip" + (tone === t ? " on" : "")} onClick={() => setTone(t)}>
            {t}
          </button>
        ))}
      </div>
      <div className="settings-field field">
        <label className="field-label">Brand voice guidelines</label>
        <textarea className="textarea" rows={4} value={guidelines} onChange={(e) => setGuidelines(e.target.value)} />
      </div>
      <div className="settings-field field">
        <label className="field-label">Words to avoid</label>
        <input className="input" value={avoid} onChange={(e) => setAvoid(e.target.value)} />
      </div>
      <button className="btn btn-spark" onClick={save}><Sparkle size={16} /> Save brand voice</button>
    </div>
  );
}

/* --------------------------------- Billing -------------------------------- */
function BillingPanel({ pushToast }: { pushToast: (m: string) => void }) {
  const sub = useApi<ApiSubscription>("subscriptions/current");
  const plans = useApi<ApiPlan[]>("subscriptions/plans");
  const usage = useApi<ApiUsage>("subscriptions/usage");
  const [busy, setBusy] = useState(false);

  const checkout = async (planId: string, cycle: "monthly" | "annual") => {
    setBusy(true);
    try {
      const res = await api.post<PaddleCheckout>("billing/checkout", {
        plan_id: planId,
        billing_cycle: cycle,
      });
      await openPaddleCheckout({
        transactionId: res.transaction_id,
        clientToken: res.client_token,
        environment: res.environment,
        successUrl: `${window.location.origin}/app/settings?billing=success`,
      });
    } catch (e) {
      pushToast(e instanceof ApiError && e.status === 503 ? e.message : errorMessage(e));
    } finally {
      setBusy(false);
    }
  };

  const portal = async () => {
    setBusy(true);
    try {
      const res = await api.post<{ url: string }>("billing/portal", {});
      window.location.href = res.url;
    } catch (e) {
      pushToast(e instanceof ApiError && e.status === 503 ? e.message : errorMessage(e));
      setBusy(false);
    }
  };

  const current = sub.data;
  const limit = (n: number) => (n < 0 ? "Unlimited" : String(n));

  return (
    <div className="settings-panel">
      <h3>Billing</h3>
      <p className="desc">Manage your plan and usage.</p>

      {sub.loading && <div className="post-sub">Loading…</div>}
      {current && (
        <div
          className="card card-pad"
          style={{
            display: "flex",
            alignItems: "center",
            gap: 16,
            marginBottom: 20,
            background: "var(--spark-tint)",
            borderColor: "color-mix(in srgb, var(--spark) 30%, transparent)",
          }}
        >
          <div>
            <div style={{ fontFamily: "var(--font-display)", fontWeight: 600, fontSize: 20 }}>
              {current.plan.name}
              {current.plan.price_monthly_cents > 0 && ` · ${dollars(current.plan.price_monthly_cents)}/mo`}
            </div>
            <div className="sub">Status: {current.status}</div>
          </div>
          <span className="spacer" />
          <button className="btn btn-secondary btn-sm" onClick={portal} disabled={busy}>Manage billing</button>
        </div>
      )}

      {usage.data && (
        <div className="settings-row">
          <div>
            <div className="lbl">This month</div>
            <div className="sub">
              {usage.data.ai_posts_used}/{limit(usage.data.ai_posts_limit)} AI posts ·{" "}
              {usage.data.connections_used}/{limit(usage.data.connections_limit)} connections ·{" "}
              {usage.data.seats_used}/{limit(usage.data.seats_limit)} seats
            </div>
          </div>
        </div>
      )}

      <h4 style={{ margin: "24px 0 12px", fontFamily: "var(--font-ui)", fontSize: 14 }}>Change plan</h4>
      <div className="price-grid" style={{ gridTemplateColumns: "1fr 1fr 1fr" }}>
        {(plans.data ?? []).map((p) => (
          <div key={p.id} className={"price-card" + (current?.plan_id === p.id ? " featured" : "")}>
            {current?.plan_id === p.id && <div className="price-pop">Current</div>}
            <div className="price-name">{p.name}</div>
            <div className="price-amt">
              {p.price_monthly_cents === 0 ? "$0" : dollars(p.price_monthly_cents)}
              <span> / mo</span>
            </div>
            <ul className="price-ticks">
              {p.features.slice(0, 4).map((f) => (
                <li key={f}>
                  <svg className="tk" width="18" height="18"><use href="#i-check" /></svg> {f}
                </li>
              ))}
            </ul>
            {p.price_monthly_cents > 0 && current?.plan_id !== p.id && (
              <button className="btn btn-spark btn-block" disabled={busy} onClick={() => checkout(p.id, "monthly")}>
                Upgrade
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

/* ------------------------------ Notifications ----------------------------- */
function NotificationsPanel({ pushToast }: { pushToast: (m: string) => void }) {
  const { data, loading, setData } = useApi<ApiNotificationPrefs>("notifications/preferences");

  const rows: [keyof ApiNotificationPrefs, string, string][] = [
    ["published", "Post published", "When a scheduled post goes live."],
    ["failed", "Post failed", "When a post can't be delivered to a platform."],
    ["weekly", "Weekly digest", "A summary of reach and engagement each Monday."],
    ["suggestions", "AI suggestions", "Best-time slots and content ideas from Postit."],
  ];

  const toggle = async (key: keyof ApiNotificationPrefs) => {
    if (!data) return;
    const next = { ...data, [key]: !data[key] };
    setData(next);
    try {
      await api.patch("notifications/preferences", { [key]: next[key] });
    } catch (e) {
      setData(data);
      pushToast(errorMessage(e));
    }
  };

  if (loading || !data) return <div className="settings-panel"><div className="post-sub">Loading…</div></div>;

  return (
    <div className="settings-panel">
      <h3>Notifications</h3>
      <p className="desc">Choose what Postit emails you about.</p>
      {rows.map(([k, label, sub]) => (
        <div key={k} className="settings-row">
          <div>
            <div className="lbl">{label}</div>
            <div className="sub">{sub}</div>
          </div>
          <Toggle on={data[k]} onClick={() => toggle(k)} />
        </div>
      ))}
    </div>
  );
}
