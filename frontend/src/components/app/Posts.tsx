"use client";

import { useCallback, useEffect, useState } from "react";
import { Icon } from "@/components/Icon";
import { PlatformLogo } from "@/components/PlatformLogo";
import { useToast } from "./providers/ToastProvider";
import { useConfirm } from "./providers/ConfirmProvider";
import { useWorkspace } from "./providers/WorkspaceProvider";
import { api } from "@/lib/api/client";
import { errorMessage } from "@/lib/api/useApi";
import type { ApiPost, Paginated, PlatformKey, PostStatus } from "@/lib/api/types";

const FILTERS: { label: string; value: PostStatus | "all" }[] = [
  { label: "All", value: "all" },
  { label: "Scheduled", value: "scheduled" },
  { label: "Published", value: "published" },
  { label: "Failed", value: "failed" },
];

function PostStatusBadge({ s }: { s: PostStatus }) {
  if (s === "scheduled")
    return (
      <span className="badge badge-ai">
        <Icon name="clock" size={12} /> Scheduled
      </span>
    );
  if (s === "published")
    return (
      <span className="badge badge-success">
        <span className="badge-dot" /> Published
      </span>
    );
  if (s === "failed" || s === "partially_failed")
    return (
      <span className="badge badge-danger">
        <Icon name="alert" size={12} /> Failed
      </span>
    );
  return (
    <span className="badge" style={{ background: "var(--surface-sunken)", color: "var(--ink-faint)" }}>
      {s}
    </span>
  );
}

function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleString(undefined, { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
}

export function Posts() {
  const pushToast = useToast();
  const confirm = useConfirm();
  const { canEdit } = useWorkspace();
  const [filter, setFilter] = useState<PostStatus | "all">("all");
  const [page] = useState(1);
  const [data, setData] = useState<Paginated<ApiPost> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    const qs = new URLSearchParams({ page: String(page), size: "20" });
    if (filter !== "all") qs.set("status", filter);
    try {
      setData(await api.get<Paginated<ApiPost>>(`posts?${qs.toString()}`));
    } catch (e) {
      setError(errorMessage(e));
    } finally {
      setLoading(false);
    }
  }, [filter, page]);

  useEffect(() => {
    void load();
  }, [load]);

  const remove = async (post: ApiPost) => {
    const live = post.status === "scheduled" || post.status === "published";
    const ok = await confirm({
      title: "Delete this post?",
      body: (
        <>
          <strong>{post.title || post.body.slice(0, 60)}</strong>
          {live
            ? " will be removed from your queue and history. Already-published posts stay live on the platforms; this only removes them from Postit."
            : " will be permanently deleted. This can't be undone."}
        </>
      ),
      confirmLabel: "Delete post",
      danger: true,
    });
    if (!ok) return;
    try {
      await api.del(`posts/${post.id}`);
      pushToast("Post deleted");
      await load();
    } catch (e) {
      pushToast(errorMessage(e));
    }
  };

  const rows = data?.items ?? [];

  return (
    <div className="view-pad">
      <div className="vh">
        <div className="vh-title">
          <h2>Posts</h2>
          <p>Everything you&apos;ve scheduled and published, across every platform.</p>
        </div>
        <div className="vh-actions">
          <div className="seg">
            {FILTERS.map((f) => (
              <button key={f.value} className={filter === f.value ? "on" : ""} onClick={() => setFilter(f.value)}>
                {f.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="posts-table">
        <div className="posts-row head">
          <span>Post</span>
          <span>Platforms</span>
          <span>Date</span>
          <span>Status</span>
          <span />
        </div>

        {loading && <div className="posts-row"><span className="post-sub">Loading…</span></div>}
        {error && <div className="posts-row"><span className="post-sub">{error}</span></div>}
        {!loading && !error && rows.length === 0 && (
          <div className="posts-row"><span className="post-sub">No posts yet. Create one in Compose.</span></div>
        )}

        {rows.map((r) => (
          <div key={r.id} className="posts-row">
            <div className="post-content">
              <span className="post-text">{r.title || r.body.slice(0, 60)}</span>
              <span className="post-sub">
                {r.targets.length} platform{r.targets.length === 1 ? "" : "s"}
              </span>
            </div>
            <div className="post-pfs">
              {r.targets.map((t) => (
                <span
                  key={t.id}
                  className={"pf pf-" + t.platform_id}
                  style={{ width: 24, height: 24, borderRadius: 7, fontSize: 11 }}
                >
                  <PlatformLogo platform={t.platform_id as PlatformKey} />
                </span>
              ))}
            </div>
            <span className="post-date">{formatDate(r.scheduled_at ?? r.published_at ?? r.created_at)}</span>
            <PostStatusBadge s={r.status} />
            {canEdit ? (
              <button
                className="icon-btn"
                style={{ width: 34, height: 34, border: 0, color: "var(--ink-faint)" }}
                title="Delete post"
                onClick={() => void remove(r)}
              >
                <Icon name="trash" size={17} />
              </button>
            ) : (
              <span />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
