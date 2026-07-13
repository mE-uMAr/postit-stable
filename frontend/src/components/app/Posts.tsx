"use client";

import { useCallback, useEffect, useState } from "react";
import { Icon } from "@/components/Icon";
import { PlatformLogo } from "@/components/PlatformLogo";
import { Sparkle } from "@/components/Sparkle";
import { useToast } from "./providers/ToastProvider";
import { useConfirm } from "./providers/ConfirmProvider";
import { useWorkspace } from "./providers/WorkspaceProvider";
import { api } from "@/lib/api/client";
import { errorMessage } from "@/lib/api/useApi";
import type { ApiPost, ApiTarget, Paginated, PlatformKey, PostStatus } from "@/lib/api/types";

const FILTERS: { label: string; value: PostStatus | "all" }[] = [
  { label: "All", value: "all" },
  { label: "Drafts", value: "draft" },
  { label: "Scheduled", value: "scheduled" },
  { label: "Published", value: "published" },
  { label: "Failed", value: "failed" },
];

function PostStatusBadge({ s }: { s: PostStatus }) {
  if (s === "draft" || s === "generating" || s === "ready")
    return (
      <span className="badge badge-draft">
        <Icon name="edit" size={12} /> Draft
      </span>
    );
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

/* ──────────────── Post Detail / Edit Modal ──────────────── */

interface PostDetailModalProps {
  post: ApiPost;
  onClose: () => void;
  onUpdated: () => void;
}

function PostDetailModal({ post, onClose, onUpdated }: PostDetailModalProps) {
  const pushToast = useToast();
  const confirm = useConfirm();
  const [body, setBody] = useState(post.body);
  const [targets, setTargets] = useState<ApiTarget[]>(post.targets);
  const [saving, setSaving] = useState(false);
  const [publishing, setPublishing] = useState(false);

  const isDraft = post.status === "draft" || post.status === "generating" || post.status === "ready";
  const hasTargets = targets.length > 0;
  const dirty = body !== post.body;

  const saveChanges = async () => {
    setSaving(true);
    try {
      await api.patch(`posts/${post.id}`, { body });
      // Save per-target edits
      for (const t of targets) {
        const orig = post.targets.find((o) => o.id === t.id);
        if (orig && orig.content !== t.content) {
          await api.put(`posts/${post.id}/targets/${t.platform_id}`, { content: t.content });
        }
      }
      pushToast("Changes saved");
      onUpdated();
    } catch (e) {
      pushToast(errorMessage(e));
    } finally {
      setSaving(false);
    }
  };

  const publishNow = async () => {
    const ok = await confirm({
      title: "Publish this post?",
      body: (
        <>
          This will publish immediately to{" "}
          <strong>
            {targets.length} platform{targets.length === 1 ? "" : "s"}
          </strong>
          . This action cannot be undone.
        </>
      ),
      confirmLabel: "Publish now",
    });
    if (!ok) return;
    setPublishing(true);
    try {
      const res = await fetch(`/api/proxy/posts/${post.id}/publish`, { method: "POST" });
      const data = await res.json().catch(() => null);
      if (!res.ok) {
        pushToast(data?.error?.message || "Couldn't publish");
        return;
      }
      pushToast(`Published to ${targets.length} platform${targets.length === 1 ? "" : "s"}`);
      onUpdated();
      onClose();
    } catch (e) {
      pushToast(errorMessage(e));
    } finally {
      setPublishing(false);
    }
  };

  const updateTarget = (platformId: string, content: string) => {
    setTargets((ts) => ts.map((t) => (t.platform_id === platformId ? { ...t, content, edited: true } : t)));
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="post-detail-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="pdm-header">
          <div className="pdm-title-row">
            <h3>{post.title || "Untitled draft"}</h3>
            <PostStatusBadge s={post.status} />
          </div>
          <button className="icon-btn pdm-close" onClick={onClose} title="Close">
            <Icon name="x" size={18} />
          </button>
        </div>

        {/* Body */}
        <div className="pdm-content">
          {/* Editable post body */}
          <div className="pdm-section">
            <label className="pdm-label">
              <Icon name="compose" size={14} /> Post body
            </label>
            {isDraft ? (
              <textarea
                className="pdm-textarea"
                value={body}
                onChange={(e) => setBody(e.target.value)}
                placeholder="Write your post…"
              />
            ) : (
              <div className="pdm-body-readonly">{body || "No content"}</div>
            )}
          </div>

          {/* Tone */}
          {post.tone && (
            <div className="pdm-meta-row">
              <span className="pdm-meta-label">Voice:</span>
              <span className="pdm-meta-value">{post.tone}</span>
            </div>
          )}

          {/* Platform variants */}
          {hasTargets && (
            <div className="pdm-section">
              <label className="pdm-label">
                <Sparkle size={14} /> Platform versions ({targets.length})
              </label>
              <div className="pdm-variants">
                {targets.map((t) => (
                  <div key={t.id} className="pdm-variant">
                    <div className="pdm-variant-head">
                      <span
                        className={"pf pf-" + t.platform_id}
                        style={{ width: 26, height: 26, borderRadius: 7, fontSize: 11 }}
                      >
                        <PlatformLogo platform={t.platform_id as PlatformKey} />
                      </span>
                      <span className="pdm-variant-name">{t.platform_id}</span>
                      {t.edited && (
                        <span className="pdm-edited-tag">
                          <Icon name="edit" size={11} /> Edited
                        </span>
                      )}
                    </div>
                    {isDraft ? (
                      <textarea
                        className="pdm-variant-text"
                        value={t.content}
                        onChange={(e) => updateTarget(t.platform_id, e.target.value)}
                      />
                    ) : (
                      <div className="pdm-variant-text readonly">{t.content}</div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {!hasTargets && isDraft && (
            <div className="pdm-empty-variants">
              <Sparkle size={28} style={{ color: "var(--ai)", opacity: 0.6 }} />
              <p>No platform versions generated yet.</p>
              <p style={{ fontSize: 12, color: "var(--ink-faint)" }}>
                Go to <strong>AI Generate</strong> or <strong>Compose</strong> to create platform-specific variants.
              </p>
            </div>
          )}
        </div>

        {/* Footer actions */}
        <div className="pdm-footer">
          <span className="pdm-date">Created {formatDate(post.created_at)}</span>
          <div className="pdm-actions">
            {isDraft && (
              <button className="btn btn-ghost" onClick={saveChanges} disabled={saving || (!dirty && true)}>
                {saving ? "Saving…" : "Save changes"}
              </button>
            )}
            {isDraft && hasTargets && (
              <button className="btn btn-spark" onClick={publishNow} disabled={publishing}>
                <Icon name="send" size={15} /> {publishing ? "Publishing…" : "Publish now"}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

/* ──────────────── Posts List ──────────────── */

export function Posts() {
  const pushToast = useToast();
  const confirm = useConfirm();
  const { canEdit } = useWorkspace();
  const [filter, setFilter] = useState<PostStatus | "all">("all");
  const [page] = useState(1);
  const [data, setData] = useState<Paginated<ApiPost> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [detailPost, setDetailPost] = useState<ApiPost | null>(null);

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

  const publishDirect = async (post: ApiPost) => {
    const ok = await confirm({
      title: "Publish this post?",
      body: (
        <>
          This will publish <strong>{post.title || post.body.slice(0, 40)}</strong> immediately to{" "}
          <strong>
            {post.targets.length} platform{post.targets.length === 1 ? "" : "s"}
          </strong>
          .
        </>
      ),
      confirmLabel: "Publish now",
    });
    if (!ok) return;
    try {
      const res = await fetch(`/api/proxy/posts/${post.id}/publish`, { method: "POST" });
      const data = await res.json().catch(() => null);
      if (!res.ok) {
        pushToast(data?.error?.message || "Couldn't publish");
        return;
      }
      pushToast(`Published to ${post.targets.length} platform${post.targets.length === 1 ? "" : "s"}`);
      await load();
    } catch (e) {
      pushToast(errorMessage(e));
    }
  };

  const isDraft = (s: PostStatus) => s === "draft" || s === "generating" || s === "ready";

  const rows = data?.items ?? [];

  return (
    <div className="view-pad">
      <div className="vh">
        <div className="vh-title">
          <h2>Posts</h2>
          <p>Manage drafts, scheduled, and published posts across every platform.</p>
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
          <div className="posts-row"><span className="post-sub">No posts yet. Create one in Compose or AI Generate.</span></div>
        )}

        {rows.map((r) => (
          <div key={r.id} className="posts-row">
            <div className="post-content">
              <span className="post-text">{r.title || r.body.slice(0, 60) || "Untitled draft"}</span>
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
              <div className="post-row-actions">
                <button
                  className="icon-btn"
                  title="View / Edit"
                  onClick={() => setDetailPost(r)}
                >
                  <Icon name={isDraft(r.status) ? "edit" : "eye"} size={16} />
                </button>
                {isDraft(r.status) && r.targets.length > 0 && (
                  <button
                    className="icon-btn post-publish-btn"
                    title="Publish now"
                    onClick={() => void publishDirect(r)}
                  >
                    <Icon name="send" size={15} />
                  </button>
                )}
                <button
                  className="icon-btn"
                  style={{ color: "var(--ink-faint)" }}
                  title="Delete post"
                  onClick={() => void remove(r)}
                >
                  <Icon name="trash" size={16} />
                </button>
              </div>
            ) : (
              <span />
            )}
          </div>
        ))}
      </div>

      {detailPost && (
        <PostDetailModal
          post={detailPost}
          onClose={() => setDetailPost(null)}
          onUpdated={() => {
            setDetailPost(null);
            void load();
          }}
        />
      )}
    </div>
  );
}
