"use client";

import { useState } from "react";
import { Icon } from "@/components/Icon";
import { Sparkle } from "@/components/Sparkle";
import { useTheme } from "./providers/ThemeProvider";
import { useToast } from "./providers/ToastProvider";

const S_TABS = ["Profile", "Workspace & team", "Brand voice", "Billing", "Notifications"];

interface TeamMember {
  name: string;
  email: string;
  role: string;
  av: string;
}

const TEAM: TeamMember[] = [
  { name: "Rina Alvarez", email: "rina@maple.co", role: "Owner", av: "RA" },
  { name: "Devon Okafor", email: "devon@maple.co", role: "Editor", av: "DO" },
  { name: "Sana Kapoor", email: "sana@maple.co", role: "Editor", av: "SK" },
  { name: "Theo Marsh", email: "theo@maple.co", role: "Viewer", av: "TM" },
];

type NotifKey = "published" | "failed" | "weekly" | "suggestions";

function Toggle({ on, onClick }: { on: boolean; onClick: () => void }) {
  return <button className={"switch" + (on ? " on" : "")} onClick={onClick} />;
}

export function Settings() {
  const { theme, toggle } = useTheme();
  const pushToast = useToast();

  const [tab, setTab] = useState("Profile");
  const [voice, setVoice] = useState("Match my brand");
  const [notifs, setNotifs] = useState<Record<NotifKey, boolean>>({
    published: true,
    failed: true,
    weekly: false,
    suggestions: true,
  });

  const notifRows: Array<[NotifKey, string, string]> = [
    ["published", "Post published", "When a scheduled post goes live."],
    ["failed", "Post failed", "When a post can't be delivered to a platform."],
    ["weekly", "Weekly digest", "A summary of reach and engagement each Monday."],
    ["suggestions", "AI suggestions", "Best-time slots and content ideas from Postit."],
  ];

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
          <div className="settings-panel">
            <h3>Profile</h3>
            <p className="desc">This is how you appear inside Postit.</p>
            <div style={{ display: "flex", alignItems: "center", gap: 18, marginBottom: 24 }}>
              <div className="avatar-lg">RA</div>
              <button className="btn btn-secondary btn-sm">
                <Icon name="upload" size={16} /> Change photo
              </button>
            </div>
            <div className="settings-field field">
              <label className="field-label">Full name</label>
              <input className="input" defaultValue="Rina Alvarez" />
            </div>
            <div className="settings-field field">
              <label className="field-label">Email</label>
              <input className="input" defaultValue="rina@maple.co" />
            </div>
            <div className="settings-row">
              <div>
                <div className="lbl">Dark mode</div>
                <div className="sub">Use the dark theme across the app.</div>
              </div>
              <Toggle on={theme === "dark"} onClick={toggle} />
            </div>
            <button className="btn btn-spark" style={{ marginTop: 20 }} onClick={() => pushToast("Profile saved")}>
              Save changes
            </button>
          </div>
        )}

        {tab === "Workspace & team" && (
          <div className="settings-panel">
            <h3>Workspace &amp; team</h3>
            <p className="desc">Maple &amp; Co · Pro plan · 4 of 5 seats used.</p>
            {TEAM.map((m, i) => (
              <div key={i} className="team-row">
                <span className="av">{m.av}</span>
                <div style={{ flex: 1 }}>
                  <div className="lbl" style={{ fontSize: 14 }}>
                    {m.name}
                  </div>
                  <div className="sub">{m.email}</div>
                </div>
                <span className="pill">{m.role}</span>
              </div>
            ))}
            <button className="btn btn-secondary" style={{ marginTop: 20 }}>
              <Icon name="plus" size={16} /> Invite member
            </button>
          </div>
        )}

        {tab === "Brand voice" && (
          <div className="settings-panel">
            <h3>Brand voice</h3>
            <p className="desc">
              The default tone Postit&apos;s AI uses when rewriting your posts. You can still override it
              per-post in the composer.
            </p>
            <div className="tone-row" style={{ marginTop: 0, marginBottom: 20 }}>
              {["Professional", "Casual", "Bold", "Match my brand"].map((t) => (
                <button key={t} className={"tone-chip" + (voice === t ? " on" : "")} onClick={() => setVoice(t)}>
                  {t}
                </button>
              ))}
            </div>
            <div className="settings-field field">
              <label className="field-label">Brand voice guidelines</label>
              <textarea
                className="textarea"
                rows={4}
                defaultValue="Warm but confident. Plain-spoken, short sentences, verbs over adjectives. We're a home-goods brand that values craft and calm. Never use exclamation marks more than once per post."
              />
            </div>
            <div className="settings-field field">
              <label className="field-label">Words to avoid</label>
              <input className="input" defaultValue="cheap, hustle, game-changer, synergy" />
            </div>
            <button className="btn btn-spark" onClick={() => pushToast("Brand voice updated")}>
              <Sparkle size={16} /> Save brand voice
            </button>
          </div>
        )}

        {tab === "Billing" && (
          <div className="settings-panel">
            <h3>Billing</h3>
            <p className="desc">You&apos;re on the Pro plan, billed annually.</p>
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
                <div style={{ fontFamily: "var(--font-display)", fontWeight: 600, fontSize: 20 }}>Pro · $15/mo</div>
                <div className="sub">Renews Mar 12, 2027 · billed annually</div>
              </div>
              <span className="spacer" />
              <button className="btn btn-secondary btn-sm">Change plan</button>
            </div>
            <div className="settings-row">
              <div className="row">
                <Icon name="card" size={20} style={{ color: "var(--ink-soft)" }} />
                <div>
                  <div className="lbl">Visa ending 4242</div>
                  <div className="sub">Expires 09/28</div>
                </div>
              </div>
              <button className="btn btn-ghost btn-sm">Update</button>
            </div>

            <div className="danger-zone">
              <h4>Danger zone</h4>
              <div className="settings-row" style={{ borderTop: 0, padding: "4px 0" }}>
                <div>
                  <div className="lbl">Delete workspace</div>
                  <div className="sub">Permanently remove Maple &amp; Co and all its posts.</div>
                </div>
                <button className="btn btn-danger btn-sm">Delete</button>
              </div>
            </div>
          </div>
        )}

        {tab === "Notifications" && (
          <div className="settings-panel">
            <h3>Notifications</h3>
            <p className="desc">Choose what Postit emails you about.</p>
            {notifRows.map(([k, label, sub]) => (
              <div key={k} className="settings-row">
                <div>
                  <div className="lbl">{label}</div>
                  <div className="sub">{sub}</div>
                </div>
                <Toggle on={notifs[k]} onClick={() => setNotifs((n) => ({ ...n, [k]: !n[k] }))} />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
