"use client";

import { useState } from "react";

import { Icon } from "@/components/Icon";
import { useToast } from "@/components/app/providers/ToastProvider";
import { api } from "@/lib/api/client";
import { errorMessage, useApi } from "@/lib/api/useApi";
import type { ApiPlan } from "@/lib/api/types";

interface FormState {
  id: string | null;
  code: string;
  name: string;
  description: string;
  price_monthly: string; // dollars
  annual_discount_percent: number;
  max_connections: number;
  max_ai_posts_monthly: number;
  max_seats: number;
  features: string; // newline separated
  is_active: boolean;
  is_public: boolean;
}

const EMPTY: FormState = {
  id: null,
  code: "",
  name: "",
  description: "",
  price_monthly: "0",
  annual_discount_percent: 20,
  max_connections: 3,
  max_ai_posts_monthly: 10,
  max_seats: 1,
  features: "",
  is_active: true,
  is_public: true,
};

function money(cents: number): string {
  return "$" + (cents / 100).toFixed(cents % 100 ? 2 : 0);
}

export default function AdminPlansPage() {
  const pushToast = useToast();
  const { data, loading, reload } = useApi<ApiPlan[]>("admin/plans");
  const [form, setForm] = useState<FormState | null>(null);
  const [saving, setSaving] = useState(false);

  const openCreate = () => setForm({ ...EMPTY });
  const openEdit = (p: ApiPlan) =>
    setForm({
      id: p.id,
      code: p.code,
      name: p.name,
      description: p.description ?? "",
      price_monthly: (p.price_monthly_cents / 100).toString(),
      annual_discount_percent: p.annual_discount_percent,
      max_connections: p.max_connections,
      max_ai_posts_monthly: p.max_ai_posts_monthly,
      max_seats: p.max_seats,
      features: p.features.join("\n"),
      is_active: p.is_active,
      is_public: p.is_public,
    });

  const save = async () => {
    if (!form) return;
    setSaving(true);
    const payload = {
      name: form.name,
      description: form.description || null,
      price_monthly_cents: Math.round(parseFloat(form.price_monthly || "0") * 100),
      annual_discount_percent: form.annual_discount_percent,
      max_connections: form.max_connections,
      max_ai_posts_monthly: form.max_ai_posts_monthly,
      max_seats: form.max_seats,
      features: form.features.split("\n").map((f) => f.trim()).filter(Boolean),
      is_active: form.is_active,
      is_public: form.is_public,
    };
    try {
      if (form.id) {
        await api.patch(`admin/plans/${form.id}`, payload);
        pushToast("Plan updated");
      } else {
        await api.post("admin/plans", { ...payload, code: form.code });
        pushToast("Plan created");
      }
      setForm(null);
      await reload();
    } catch (e) {
      pushToast(errorMessage(e));
    } finally {
      setSaving(false);
    }
  };

  const archive = async (id: string) => {
    try {
      await api.del(`admin/plans/${id}`);
      await reload();
      pushToast("Plan archived");
    } catch (e) {
      pushToast(errorMessage(e));
    }
  };

  const annualCents = form
    ? Math.round(parseFloat(form.price_monthly || "0") * 100 * 12 * (100 - form.annual_discount_percent) / 100)
    : 0;

  return (
    <div className="view-pad">
      <div className="vh">
        <div className="vh-title">
          <h2>Plans</h2>
          <p>Create plans, set monthly price and annual discount, and define limits.</p>
        </div>
        <div className="vh-actions">
          <button className="btn btn-spark" onClick={openCreate}>
            <Icon name="plus" size={17} /> New plan
          </button>
        </div>
      </div>

      {loading && <div className="post-sub">Loading…</div>}

      <div className="conn-grid">
        {(data ?? []).map((p) => (
          <div key={p.id} className="conn-card" style={{ opacity: p.is_active ? 1 : 0.55 }}>
            <div className="conn-top">
              <div>
                <div className="conn-name">{p.name}</div>
                <span className="post-sub">{p.code}</span>
              </div>
              <span className="spacer" />
              <span className="badge badge-spark">{money(p.price_monthly_cents)}/mo</span>
            </div>
            <div className="post-sub">
              {money(p.price_annual_cents)}/yr · {p.annual_discount_percent}% off · seats {p.max_seats} · AI{" "}
              {p.max_ai_posts_monthly < 0 ? "∞" : p.max_ai_posts_monthly} · conns{" "}
              {p.max_connections < 0 ? "∞" : p.max_connections}
            </div>
            <div className="conn-foot">
              <button className="btn btn-secondary btn-sm" onClick={() => openEdit(p)}>
                Edit
              </button>
              <button className="btn btn-ghost btn-sm" style={{ color: "var(--ink-faint)" }} onClick={() => archive(p.id)}>
                Archive
              </button>
            </div>
          </div>
        ))}
      </div>

      {form && (
        <div className="modal-overlay" onClick={() => setForm(null)}>
          <div className="modal" style={{ maxWidth: 540 }} onClick={(e) => e.stopPropagation()}>
            <div className="modal-head">
              <h3>{form.id ? "Edit plan" : "New plan"}</h3>
              <p>Annual price is derived from the monthly price and discount.</p>
            </div>
            <div className="modal-body" style={{ display: "grid", gap: 12, maxHeight: "60vh", overflowY: "auto" }}>
              {!form.id && (
                <Field label="Code (unique, e.g. pro)">
                  <input className="input" value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value })} />
                </Field>
              )}
              <Field label="Name">
                <input className="input" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
              </Field>
              <Field label="Description">
                <input className="input" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
              </Field>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                <Field label="Monthly price ($)">
                  <input className="input" type="number" value={form.price_monthly} onChange={(e) => setForm({ ...form, price_monthly: e.target.value })} />
                </Field>
                <Field label="Annual discount (%)">
                  <input className="input" type="number" value={form.annual_discount_percent} onChange={(e) => setForm({ ...form, annual_discount_percent: Number(e.target.value) })} />
                </Field>
              </div>
              <div className="post-sub">Annual total: {money(annualCents)}</div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12 }}>
                <Field label="Max connections">
                  <input className="input" type="number" value={form.max_connections} onChange={(e) => setForm({ ...form, max_connections: Number(e.target.value) })} />
                </Field>
                <Field label="AI / month (-1 = ∞)">
                  <input className="input" type="number" value={form.max_ai_posts_monthly} onChange={(e) => setForm({ ...form, max_ai_posts_monthly: Number(e.target.value) })} />
                </Field>
                <Field label="Seats">
                  <input className="input" type="number" value={form.max_seats} onChange={(e) => setForm({ ...form, max_seats: Number(e.target.value) })} />
                </Field>
              </div>
              <Field label="Features (one per line)">
                <textarea className="textarea" rows={4} value={form.features} onChange={(e) => setForm({ ...form, features: e.target.value })} />
              </Field>
              <label className="checkbox-row">
                <input type="checkbox" checked={form.is_active} onChange={(e) => setForm({ ...form, is_active: e.target.checked })} /> Active
              </label>
              <label className="checkbox-row">
                <input type="checkbox" checked={form.is_public} onChange={(e) => setForm({ ...form, is_public: e.target.checked })} /> Public (shown on pricing)
              </label>
            </div>
            <div className="modal-foot">
              <button className="btn btn-ghost" onClick={() => setForm(null)}>
                Cancel
              </button>
              <button className="btn btn-spark" onClick={save} disabled={saving}>
                {form.id ? "Save plan" : "Create plan"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="field">
      <label className="field-label">{label}</label>
      {children}
    </div>
  );
}
