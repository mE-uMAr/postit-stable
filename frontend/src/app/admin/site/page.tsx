"use client";

import { useEffect, useState, type ReactNode } from "react";

import { Icon } from "@/components/Icon";
import { useToast } from "@/components/app/providers/ToastProvider";
import { api } from "@/lib/api/client";
import { errorMessage } from "@/lib/api/useApi";
import type { SiteContent } from "@/lib/api/types";

export default function AdminSitePage() {
  const pushToast = useToast();
  const [c, setC] = useState<SiteContent | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        setC(await api.get<SiteContent>("admin/site"));
      } catch (e) {
        pushToast(errorMessage(e));
      } finally {
        setLoading(false);
      }
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (loading || !c) {
    return (
      <div className="view-pad">
        <div className="post-sub">Loading site content…</div>
      </div>
    );
  }

  const save = async () => {
    setSaving(true);
    try {
      const next = await api.put<SiteContent>("admin/site", c as unknown as Record<string, unknown>);
      setC(next);
      pushToast("Site content published.");
    } catch (e) {
      pushToast(errorMessage(e));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="view-pad">
      <div className="vh">
        <div className="vh-title">
          <h2>Site content</h2>
          <p>Edit the public marketing site. Changes publish instantly.</p>
        </div>
      </div>

      <div className="cms">
        {/* Announcement bar */}
        <section className="cms-card">
          <h3>Announcement bar</h3>
          <p className="hint">A thin banner across the top of the landing page.</p>
          <label className="cms-toggle">
            <input
              type="checkbox"
              checked={c.announcement.enabled}
              onChange={(e) => setC({ ...c, announcement: { ...c.announcement, enabled: e.target.checked } })}
            />
            Show announcement
          </label>
          <div className="cms-field" style={{ marginTop: 12 }}>
            <label>Text</label>
            <input
              className="input"
              value={c.announcement.text}
              onChange={(e) => setC({ ...c, announcement: { ...c.announcement, text: e.target.value } })}
            />
          </div>
        </section>

        {/* Hero */}
        <section className="cms-card">
          <h3>Hero</h3>
          <div className="cms-field">
            <label>Eyebrow</label>
            <input
              className="input"
              value={c.hero.eyebrow}
              onChange={(e) => setC({ ...c, hero: { ...c.hero, eyebrow: e.target.value } })}
            />
          </div>
          <div className="cms-field">
            <label>Title</label>
            <input
              className="input"
              value={c.hero.title}
              onChange={(e) => setC({ ...c, hero: { ...c.hero, title: e.target.value } })}
            />
          </div>
          <div className="cms-field">
            <label>Subtitle</label>
            <textarea
              className="input"
              rows={2}
              value={c.hero.subtitle}
              onChange={(e) => setC({ ...c, hero: { ...c.hero, subtitle: e.target.value } })}
            />
          </div>
          <div className="cms-row">
            <div className="cms-field">
              <label>Primary button label</label>
              <input
                className="input"
                value={c.hero.primary_cta.label}
                onChange={(e) =>
                  setC({ ...c, hero: { ...c.hero, primary_cta: { ...c.hero.primary_cta, label: e.target.value } } })
                }
              />
            </div>
            <div className="cms-field">
              <label>Primary button link</label>
              <input
                className="input"
                value={c.hero.primary_cta.href}
                onChange={(e) =>
                  setC({ ...c, hero: { ...c.hero, primary_cta: { ...c.hero.primary_cta, href: e.target.value } } })
                }
              />
            </div>
          </div>
        </section>

        {/* Logos */}
        <section className="cms-card">
          <h3>Logo strip</h3>
          <p className="hint">Comma-separated company names shown under the hero.</p>
          <div className="cms-field">
            <input
              className="input"
              value={c.logos.join(", ")}
              onChange={(e) => setC({ ...c, logos: e.target.value.split(",").map((s) => s.trim()).filter(Boolean) })}
            />
          </div>
        </section>

        {/* Features */}
        <RepeatSection
          title="Features"
          items={c.features}
          onAdd={() => setC({ ...c, features: [...c.features, { icon: "compose", title: "", body: "" }] })}
          onRemove={(i) => setC({ ...c, features: c.features.filter((_, j) => j !== i) })}
          render={(f, i) => (
            <>
              <div className="cms-field">
                <label>Title</label>
                <input
                  className="input"
                  value={f.title}
                  onChange={(e) => {
                    const features = [...c.features];
                    features[i] = { ...f, title: e.target.value };
                    setC({ ...c, features });
                  }}
                />
              </div>
              <div className="cms-field">
                <label>Body</label>
                <textarea
                  className="input"
                  rows={2}
                  value={f.body}
                  onChange={(e) => {
                    const features = [...c.features];
                    features[i] = { ...f, body: e.target.value };
                    setC({ ...c, features });
                  }}
                />
              </div>
            </>
          )}
        />

        {/* Testimonials */}
        <RepeatSection
          title="Testimonials"
          items={c.testimonials}
          onAdd={() => setC({ ...c, testimonials: [...c.testimonials, { quote: "", name: "", role: "" }] })}
          onRemove={(i) => setC({ ...c, testimonials: c.testimonials.filter((_, j) => j !== i) })}
          render={(t, i) => (
            <>
              <div className="cms-field">
                <label>Quote</label>
                <textarea
                  className="input"
                  rows={2}
                  value={t.quote}
                  onChange={(e) => {
                    const testimonials = [...c.testimonials];
                    testimonials[i] = { ...t, quote: e.target.value };
                    setC({ ...c, testimonials });
                  }}
                />
              </div>
              <div className="cms-row">
                <div className="cms-field">
                  <label>Name</label>
                  <input
                    className="input"
                    value={t.name}
                    onChange={(e) => {
                      const testimonials = [...c.testimonials];
                      testimonials[i] = { ...t, name: e.target.value };
                      setC({ ...c, testimonials });
                    }}
                  />
                </div>
                <div className="cms-field">
                  <label>Role</label>
                  <input
                    className="input"
                    value={t.role}
                    onChange={(e) => {
                      const testimonials = [...c.testimonials];
                      testimonials[i] = { ...t, role: e.target.value };
                      setC({ ...c, testimonials });
                    }}
                  />
                </div>
              </div>
            </>
          )}
        />

        {/* FAQ */}
        <RepeatSection
          title="FAQ"
          items={c.faq}
          onAdd={() => setC({ ...c, faq: [...c.faq, { q: "", a: "" }] })}
          onRemove={(i) => setC({ ...c, faq: c.faq.filter((_, j) => j !== i) })}
          render={(f, i) => (
            <>
              <div className="cms-field">
                <label>Question</label>
                <input
                  className="input"
                  value={f.q}
                  onChange={(e) => {
                    const faq = [...c.faq];
                    faq[i] = { ...f, q: e.target.value };
                    setC({ ...c, faq });
                  }}
                />
              </div>
              <div className="cms-field">
                <label>Answer</label>
                <textarea
                  className="input"
                  rows={2}
                  value={f.a}
                  onChange={(e) => {
                    const faq = [...c.faq];
                    faq[i] = { ...f, a: e.target.value };
                    setC({ ...c, faq });
                  }}
                />
              </div>
            </>
          )}
        />

        {/* Flags */}
        <section className="cms-card">
          <h3>Feature flags</h3>
          <label className="cms-toggle">
            <input
              type="checkbox"
              checked={c.flags.show_pricing}
              onChange={(e) => setC({ ...c, flags: { ...c.flags, show_pricing: e.target.checked } })}
            />
            Show pricing section
          </label>
          <label className="cms-toggle" style={{ marginTop: 10 }}>
            <input
              type="checkbox"
              checked={c.flags.social_auth}
              onChange={(e) => setC({ ...c, flags: { ...c.flags, social_auth: e.target.checked } })}
            />
            Enable social sign-in buttons
          </label>
        </section>

        <div className="cms-bar">
          <button className={"btn btn-spark" + (saving ? " is-loading" : "")} onClick={save} disabled={saving}>
            {saving ? <span className="spin" /> : "Publish changes"}
          </button>
          <span className="post-sub">Live on the public site immediately.</span>
        </div>
      </div>
    </div>
  );
}

function RepeatSection<T>({
  title,
  items,
  onAdd,
  onRemove,
  render,
}: {
  title: string;
  items: T[];
  onAdd: () => void;
  onRemove: (i: number) => void;
  render: (item: T, i: number) => ReactNode;
}) {
  return (
    <section className="cms-card">
      <h3>{title}</h3>
      {items.map((item, i) => (
        <div key={i} className="cms-repeat-item">
          {render(item, i)}
          <button
            className="btn btn-ghost btn-sm"
            style={{ marginTop: 4 }}
            onClick={() => onRemove(i)}
          >
            <Icon name="trash" size={15} /> Remove
          </button>
        </div>
      ))}
      <button className="btn btn-secondary btn-sm" onClick={onAdd}>
        <Icon name="plus" size={15} /> Add {title.replace(/s$/, "").toLowerCase()}
      </button>
    </section>
  );
}
