"use client";

import { useToast } from "@/components/app/providers/ToastProvider";
import { api } from "@/lib/api/client";
import { errorMessage, useApi } from "@/lib/api/useApi";
import type { AdminSubscription, ApiPlan, Paginated } from "@/lib/api/types";

function money(cents: number): string {
  return cents === 0 ? "—" : "$" + (cents / 100).toFixed(0);
}

export default function AdminSubscriptionsPage() {
  const pushToast = useToast();
  const subs = useApi<Paginated<AdminSubscription>>("admin/subscriptions?page=1&size=50");
  const plans = useApi<ApiPlan[]>("admin/plans");

  const override = async (subId: string, planId: string) => {
    try {
      await api.post(`admin/subscriptions/${subId}/override`, { plan_id: planId });
      await subs.reload();
      pushToast("Subscription updated");
    } catch (e) {
      pushToast(errorMessage(e));
    }
  };

  const rows = subs.data?.items ?? [];

  return (
    <div className="view-pad">
      <div className="vh">
        <div className="vh-title">
          <h2>Subscriptions</h2>
          <p>{subs.data ? `${subs.data.total} workspaces` : "—"}</p>
        </div>
      </div>

      <div className="posts-table">
        <div className="posts-row head" style={{ gridTemplateColumns: "minmax(0,2fr) 120px 110px 100px 1fr" }}>
          <span>Workspace</span>
          <span>Plan</span>
          <span>Status</span>
          <span>MRR</span>
          <span>Override</span>
        </div>
        {subs.loading && <div className="posts-row"><span className="post-sub">Loading…</span></div>}
        {rows.map((s) => (
          <div key={s.id} className="posts-row" style={{ gridTemplateColumns: "minmax(0,2fr) 120px 110px 100px 1fr" }}>
            <div className="post-content">
              <span className="post-text">{s.workspace_name}</span>
              <span className="post-sub">{s.billing_cycle}</span>
            </div>
            <span className="post-date">{s.plan_name}</span>
            <span className="badge badge-ai">{s.status}</span>
            <span className="post-date">{money(s.mrr_cents)}/mo</span>
            <select
              className="input"
              style={{ maxWidth: 160 }}
              defaultValue=""
              onChange={(e) => e.target.value && override(s.id, e.target.value)}
            >
              <option value="" disabled>
                Move to…
              </option>
              {(plans.data ?? []).map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
          </div>
        ))}
      </div>
    </div>
  );
}
