"use client";

import { useEffect, useState } from "react";

import { Icon } from "@/components/Icon";
import { useToast } from "@/components/app/providers/ToastProvider";
import { useConfirm } from "@/components/app/providers/ConfirmProvider";
import { api } from "@/lib/api/client";
import { errorMessage } from "@/lib/api/useApi";
import type { AdminUser, Paginated } from "@/lib/api/types";

export default function AdminUsersPage() {
  const pushToast = useToast();
  const confirm = useConfirm();
  const [q, setQ] = useState("");
  const [query, setQuery] = useState("");
  const [data, setData] = useState<Paginated<AdminUser> | null>(null);
  const [loading, setLoading] = useState(true);

  const load = async (search: string) => {
    setLoading(true);
    try {
      const qs = new URLSearchParams({ page: "1", size: "50" });
      if (search) qs.set("q", search);
      setData(await api.get<Paginated<AdminUser>>(`admin/users?${qs}`));
    } catch (e) {
      pushToast(errorMessage(e));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load(query);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [query]);

  const update = async (id: string, patch: Record<string, boolean>) => {
    try {
      await api.patch(`admin/users/${id}`, patch);
      await load(query);
    } catch (e) {
      pushToast(errorMessage(e));
    }
  };

  const remove = async (id: string) => {
    try {
      await api.del(`admin/users/${id}`);
      await load(query);
      pushToast("User deleted");
    } catch (e) {
      pushToast(errorMessage(e));
    }
  };

  // --- confirmed actions ---
  const toggleActive = async (u: AdminUser) => {
    if (u.is_active) {
      const ok = await confirm({
        title: `Disable ${u.full_name}?`,
        body: (
          <>
            They&apos;ll be signed out and blocked from logging in until re-enabled. Their workspaces
            and posts are kept.
          </>
        ),
        confirmLabel: "Disable account",
        danger: true,
      });
      if (!ok) return;
    }
    await update(u.id, { is_active: !u.is_active });
  };

  const toggleAdmin = async (u: AdminUser) => {
    const granting = !u.is_superuser;
    const ok = await confirm({
      title: granting ? `Make ${u.full_name} an admin?` : `Remove admin from ${u.full_name}?`,
      body: granting
        ? "Platform admins get full access to the admin console: every user, workspace, plan, and billing record."
        : "They'll lose access to the admin console and return to a normal workspace user.",
      confirmLabel: granting ? "Grant admin" : "Remove admin",
      danger: !granting,
    });
    if (!ok) return;
    await update(u.id, { is_superuser: !u.is_superuser });
  };

  const confirmRemove = async (u: AdminUser) => {
    const ok = await confirm({
      title: `Delete ${u.full_name}?`,
      body: (
        <>
          This deactivates the account for <strong>{u.email}</strong> and removes them from the
          platform. This can&apos;t be undone from here.
        </>
      ),
      confirmLabel: "Delete user",
      danger: true,
    });
    if (ok) await remove(u.id);
  };

  const rows = data?.items ?? [];

  return (
    <div className="view-pad">
      <div className="vh">
        <div className="vh-title">
          <h2>Users</h2>
          <p>{data ? `${data.total} accounts` : "-"}</p>
        </div>
        <div className="vh-actions">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              setQuery(q);
            }}
            className="topbar-search"
            style={{ width: 280 }}
          >
            <Icon name="search" size={17} />
            <input placeholder="Search name or email…" value={q} onChange={(e) => setQ(e.target.value)} />
          </form>
        </div>
      </div>

      <div className="posts-table">
        <div className="posts-row head" style={{ gridTemplateColumns: "minmax(0,2fr) 120px 110px 110px 1fr" }}>
          <span>User</span>
          <span>Workspaces</span>
          <span>Status</span>
          <span>Role</span>
          <span>Actions</span>
        </div>
        {loading && <div className="posts-row"><span className="post-sub">Loading…</span></div>}
        {!loading && rows.length === 0 && <div className="posts-row"><span className="post-sub">No users.</span></div>}
        {rows.map((u) => (
          <div key={u.id} className="posts-row" style={{ gridTemplateColumns: "minmax(0,2fr) 120px 110px 110px 1fr" }}>
            <div className="post-content">
              <span className="post-text">{u.full_name}</span>
              <span className="post-sub">{u.email}</span>
            </div>
            <span className="post-date">{u.workspace_count}</span>
            <span className={"badge " + (u.is_active ? "badge-success" : "badge-danger")}>
              <span className="badge-dot" /> {u.is_active ? "Active" : "Disabled"}
            </span>
            <span className={"badge " + (u.is_superuser ? "badge-ai" : "")} style={!u.is_superuser ? { background: "var(--surface-sunken)", color: "var(--ink-faint)" } : undefined}>
              {u.is_superuser ? "Admin" : "User"}
            </span>
            <div className="row" style={{ gap: 6, flexWrap: "wrap" }}>
              <button className="btn btn-ghost btn-sm" onClick={() => void toggleActive(u)}>
                {u.is_active ? "Disable" : "Enable"}
              </button>
              <button className="btn btn-ghost btn-sm" onClick={() => void toggleAdmin(u)}>
                {u.is_superuser ? "Demote" : "Promote"}
              </button>
              <button className="btn btn-ghost btn-sm" style={{ color: "var(--danger)" }} onClick={() => void confirmRemove(u)}>
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
