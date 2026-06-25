"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { Icon } from "@/components/Icon";
import { Sparkle } from "@/components/Sparkle";
import { PlatformLogo } from "@/components/PlatformLogo";
import { api } from "@/lib/api/client";
import { errorMessage, useApi } from "@/lib/api/useApi";
import type { ApiConnection, ApiPlatform, ApiPost, ApiTarget, PlatformKey } from "@/lib/api/types";
import { useToast } from "./providers/ToastProvider";
import { ConfirmModal, type ConfirmMode } from "./ConfirmModal";

const TONES = ["Professional", "Casual", "Bold", "Match my brand"];

interface MediaItem {
  type: "image" | "video";
  key: string;
  file: File; // held client-side; streamed to platforms only at publish time
  previewUrl: string; // object URL for local preview
}

interface Variant {
  content: string;
  edited: boolean;
}
type Variants = Record<string, Variant>;

interface Eligibility {
  ok: boolean;
  reason?: string;
  warn?: string;
}

function eligibility(
  p: ApiPlatform,
  { hasMedia, hasVideo, charCount }: { hasMedia: boolean; hasVideo: boolean; charCount: number },
): Eligibility {
  if (p.requires_video && !hasVideo) return { ok: false, reason: "Needs a video - disabled for this post." };
  if (p.requires_media && !hasMedia) return { ok: false, reason: `${p.name} requires an image or video.` };
  if (p.char_limit && charCount > p.char_limit) return { ok: true, warn: `Over ${p.char_limit} characters - Postit will trim.` };
  return { ok: true };
}

interface PreviewCardProps {
  platform: ApiPlatform;
  author: string;
  handle: string;
  variant: Variant;
  idx: number;
  onEdit: (platformId: string, text: string) => void;
  onRegen: (platformId: string) => void;
  shimmering: boolean;
}

function NativePreviewCard({ platform, author, handle, variant, idx, onEdit, onRegen, shimmering }: PreviewCardProps) {
  const ref = useRef<HTMLDivElement>(null);
  return (
    <div className={"npc in" + (shimmering ? " shimmering" : "")} style={{ animationDelay: idx * 60 + "ms" }}>
      <div className="npc-top">
        <div className="npc-av" style={{ background: `var(--pf-${platform.id})` }}>
          <PlatformLogo platform={platform.id as PlatformKey} />
        </div>
        <div className="npc-id">
          <div className="nm">{author}</div>
          <div className="hd">{handle}</div>
        </div>
        <span className={"pf pf-" + platform.id + " npc-pfbadge"} style={{ width: 24, height: 24, borderRadius: 7, fontSize: 11 }}>
          <PlatformLogo platform={platform.id as PlatformKey} />
        </span>
      </div>
      <div
        className="npc-body"
        contentEditable
        suppressContentEditableWarning
        ref={ref}
        onBlur={() => {
          if (ref.current && ref.current.innerText !== variant.content) onEdit(platform.id, ref.current.innerText);
        }}
      >
        {variant.content}
      </div>
      {(platform.requires_media || platform.requires_video) && (
        <div className="npc-media placeholder" style={{ borderRadius: 0 }}>
          {platform.requires_video ? "video frame" : "image"}
        </div>
      )}
      <div className="npc-actions">
        <span className="a"><Icon name="heart" size={16} /> 248</span>
        <span className="a"><Icon name="comment" size={16} /> 19</span>
        <span className="a"><Icon name="repost" size={16} /> 32</span>
        <span className="a" style={{ marginLeft: "auto" }}><Icon name="send" size={16} /></span>
      </div>
      <div className="npc-foot">
        {variant.edited ? (
          <span className="edited"><Icon name="edit" size={13} /> Edited</span>
        ) : (
          <span className="edited" style={{ color: "var(--ai)" }}><Sparkle size={13} /> AI generated</span>
        )}
        <button className="regen" onClick={() => onRegen(platform.id)}>
          <Icon name="refresh" size={14} /> Regenerate
        </button>
      </div>
    </div>
  );
}

export function Compose() {
  const pushToast = useToast();
  const platformsApi = useApi<ApiPlatform[]>("platforms");
  const connectionsApi = useApi<ApiConnection[]>("connections");

  const platforms = useMemo(() => platformsApi.data ?? [], [platformsApi.data]);
  const connByPlatform = useMemo(() => {
    const m = new Map<string, ApiConnection>();
    (connectionsApi.data ?? []).forEach((c) => m.set(c.platform_id, c));
    return m;
  }, [connectionsApi.data]);

  const [text, setText] = useState("");
  const [tone, setTone] = useState("Match my brand");
  const [media, setMedia] = useState<MediaItem[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  // No platform is selectable until the user has actually connected its account.
  // Starts empty and is seeded once from real connections below.
  const [selected, setSelected] = useState<Set<string>>(() => new Set());
  const seededRef = useRef(false);
  const [postId, setPostId] = useState<string | null>(null);
  const [variants, setVariants] = useState<Variants | null>(null);
  const [generating, setGenerating] = useState(false);
  const [shimmerKey, setShimmerKey] = useState<string | null>(null);
  const [modal, setModal] = useState<ConfirmMode | null>(null);

  const hasMedia = media.length > 0;
  const hasVideo = media.some((m) => m.type === "video");
  const charCount = text.length;

  const platformById = useMemo(() => {
    const m = new Map<string, ApiPlatform>();
    platforms.forEach((p) => m.set(p.id, p));
    return m;
  }, [platforms]);

  const elig = (id: string): Eligibility => {
    const p = platformById.get(id);
    if (!p) return { ok: false };
    // A platform is only postable once its account is connected via OAuth.
    const conn = connByPlatform.get(id);
    if (!conn || conn.status !== "connected")
      return { ok: false, reason: `Connect your ${p.name} account in Connections first.` };
    return eligibility(p, { hasMedia, hasVideo, charCount });
  };

  // Seed the default selection from the platforms the user actually has connected
  // (text-capable ones, since a fresh post has no media yet). Runs once after both
  // platforms and connections have loaded; fresh users start with nothing selected.
  useEffect(() => {
    if (seededRef.current || !platformsApi.data || !connectionsApi.data) return;
    seededRef.current = true;
    const defaults = platforms.filter((p) => {
      const c = connByPlatform.get(p.id);
      if (!c || c.status !== "connected") return false;
      return !p.requires_media && !p.requires_video;
    });
    if (defaults.length) setSelected(new Set(defaults.map((p) => p.id)));
  }, [platformsApi.data, connectionsApi.data, platforms, connByPlatform]);

  const toggle = (id: string) => {
    if (!elig(id).ok) return;
    setSelected((s) => {
      const n = new Set(s);
      if (n.has(id)) n.delete(id);
      else n.add(id);
      return n;
    });
  };
  const selectAllEligible = () => setSelected(new Set(platforms.filter((p) => elig(p.id).ok).map((p) => p.id)));

  const addFiles = (files: FileList | null) => {
    if (!files?.length) return;
    const items: MediaItem[] = Array.from(files).map((file) => ({
      type: file.type.startsWith("video/") ? "video" : "image",
      key: `${file.name}-${Date.now()}-${Math.random()}`,
      file,
      previewUrl: URL.createObjectURL(file),
    }));
    setMedia((m) => [...m, ...items]);
  };
  const removeMedia = (key: string) =>
    setMedia((m) => {
      const found = m.find((x) => x.key === key);
      if (found) URL.revokeObjectURL(found.previewUrl);
      return m.filter((x) => x.key !== key);
    });

  const eligibleSelected = [...selected].filter((k) => elig(k).ok);

  const authorFor = (id: string) => connByPlatform.get(id)?.display_name ?? platformById.get(id)?.name ?? id;
  const handleFor = (id: string) => connByPlatform.get(id)?.handle ?? "Preview";

  const ensurePost = async (): Promise<string> => {
    const payload = {
      body: text,
      tone,
      media: media.map((m) => ({ type: m.type })),
    };
    if (postId) {
      await api.patch(`posts/${postId}`, payload);
      return postId;
    }
    const created = await api.post<ApiPost>("posts", payload);
    setPostId(created.id);
    return created.id;
  };

  const generate = async () => {
    if (!text.trim() || eligibleSelected.length === 0) return;
    setGenerating(true);
    try {
      const id = await ensurePost();
      const updated = await api.post<ApiPost>(`posts/${id}/generate`, { platforms: eligibleSelected });
      const v: Variants = {};
      updated.targets.forEach((t: ApiTarget) => {
        v[t.platform_id] = { content: t.content, edited: t.edited };
      });
      setVariants(v);
    } catch (e) {
      pushToast(errorMessage(e));
    } finally {
      setGenerating(false);
    }
  };

  const onEdit = async (platformId: string, content: string) => {
    setVariants((v) => (v ? { ...v, [platformId]: { content, edited: true } } : v));
    if (!postId) return;
    try {
      await api.put(`posts/${postId}/targets/${platformId}`, { content });
    } catch (e) {
      pushToast(errorMessage(e));
    }
  };

  const onRegen = async (platformId: string) => {
    if (!postId) return;
    setShimmerKey(platformId);
    try {
      const t = await api.post<ApiTarget>(`posts/${postId}/targets/${platformId}/regenerate`);
      setVariants((v) => (v ? { ...v, [platformId]: { content: t.content, edited: t.edited } } : v));
    } catch (e) {
      pushToast(errorMessage(e));
    } finally {
      setShimmerKey(null);
    }
  };

  const saveDraft = async () => {
    try {
      await ensurePost();
      pushToast("Draft saved");
    } catch (e) {
      pushToast(errorMessage(e));
    }
  };

  const confirmAction = async () => {
    setModal(null);
    if (!postId) return;
    try {
      // Media is streamed with the publish request (not stored server-side).
      const fd = new FormData();
      media.forEach((m) => fd.append("files", m.file, m.file.name));
      const res = await fetch(`/api/posts/${postId}/publish`, { method: "POST", body: fd });
      const data = await res.json().catch(() => null);
      if (!res.ok) {
        pushToast(data?.error?.message || "Couldn't publish");
        return;
      }
      pushToast(`Posted to ${postCount} platforms`);
    } catch (e) {
      pushToast(errorMessage(e));
    }
  };

  const shownKeys = variants ? Object.keys(variants).filter((k) => selected.has(k) && elig(k).ok) : [];
  const xLimit = platformById.get("x")?.char_limit ?? 280;
  const overX = selected.has("x") && charCount > xLimit;
  const postCount = eligibleSelected.length;
  const canPublish = Boolean(variants && shownKeys.length > 0);

  return (
    <div className="compose-grid">
      {/* LEFT - composer + selector */}
      <div className="compose-left">
        <div className="composer-card">
          <div className="composer-toolbar">
            <button className="tool-btn" title="Bold"><Icon name="bold" size={18} /></button>
            <button className="tool-btn" title="Italic"><Icon name="italic" size={18} /></button>
            <button className="tool-btn" title="Link"><Icon name="link" size={18} /></button>
            <span className="spacer" />
            <span className={"char-meter" + (overX ? " warn" : "")}>
              {selected.has("x") ? `${charCount} / ${xLimit} · X` : `${charCount} chars`}
            </span>
          </div>
          <textarea
            className="compose-textarea"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="What do you want to say?"
          />
          {media.length > 0 && (
            <div className="media-thumbs">
              {media.map((m) => (
                <div key={m.key} className="media-thumb">
                  {m.type === "video" ? (
                    <video src={m.previewUrl} muted />
                  ) : (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img src={m.previewUrl} alt="" />
                  )}
                  <button className="rm" onClick={() => removeMedia(m.key)}>
                    <Icon name="x" size={12} />
                  </button>
                </div>
              ))}
            </div>
          )}
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*,video/*"
            multiple
            hidden
            onChange={(e) => {
              addFiles(e.target.files);
              e.target.value = "";
            }}
          />
          <div className="media-zone" onClick={() => fileInputRef.current?.click()}>
            <Icon name="image" size={18} />
            <span>Click to add images or video</span>
          </div>
        </div>

        <div className="tone-row">
          <span className="tone-label">Voice</span>
          {TONES.map((t) => (
            <button key={t} className={"tone-chip" + (tone === t ? " on" : "")} onClick={() => setTone(t)}>
              {t}
            </button>
          ))}
        </div>

        <button
          className="btn btn-ai btn-lg generate-btn"
          onClick={generate}
          disabled={generating || !text.trim() || eligibleSelected.length === 0}
        >
          {generating ? (
            <><span className="spin" /> Generating…</>
          ) : (
            <><Sparkle size={17} /> Generate platform versions</>
          )}
        </button>

        <div className="psel">
          <div className="psel-head">
            <span className="ttl">Post to</span>
            <button className="all" onClick={selectAllEligible}>Select all eligible</button>
          </div>
          <div className="psel-grid">
            {platforms.map((p) => {
              const e = elig(p.id);
              const sel = selected.has(p.id);
              const warn = sel && e.warn;
              return (
                <button
                  key={p.id}
                  className={"pchip" + (sel ? " is-selected" : "") + (!e.ok ? " is-disabled" : "") + (warn ? " is-warning" : "")}
                  onClick={() => toggle(p.id)}
                  title={e.reason || e.warn || ""}
                >
                  <span className={"pf-dot pf-" + p.id} />
                  {p.name}
                  {!e.ok && <Icon name="alert" size={14} style={{ marginLeft: 2, color: "var(--ink-faint)" }} />}
                  {warn && <Icon name="alert" size={14} style={{ marginLeft: 2, color: "var(--spark-deep)" }} />}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* RIGHT - preview grid */}
      <div className="compose-right">
        <div className="preview-head">
          <span className="ttl">
            Live preview · {shownKeys.length || postCount} platform{(shownKeys.length || postCount) === 1 ? "" : "s"}
          </span>
          {variants && (
            <button
              className="all"
              style={{ color: "var(--ai)", fontWeight: 600, fontSize: 13, background: "none", border: 0 }}
              onClick={generate}
            >
              <Icon name="refresh" size={14} /> Regenerate all
            </button>
          )}
        </div>

        {generating && (
          <div className="preview-list">
            {eligibleSelected.map((k) => (
              <div key={k} className="npc shimmering in" style={{ minHeight: 150 }}>
                <div className="npc-top">
                  <div className="npc-av" style={{ background: "#ddd", color: "var(--ink-faint)" }}>
                    <PlatformLogo platform={k as PlatformKey} />
                  </div>
                  <div className="npc-id">
                    <div className="nm" style={{ color: "var(--ink-faint)" }}>{authorFor(k)}</div>
                  </div>
                </div>
                <div className="npc-body" style={{ color: "var(--ink-faint)" }}>
                  Writing a native {platformById.get(k)?.name} version…
                </div>
              </div>
            ))}
          </div>
        )}

        {!generating && shownKeys.length > 0 && variants && (
          <div className="preview-list">
            {shownKeys.map((k, i) => (
              <NativePreviewCard
                key={k}
                platform={platformById.get(k)!}
                author={authorFor(k)}
                handle={handleFor(k)}
                variant={variants[k]}
                idx={i}
                onEdit={onEdit}
                onRegen={onRegen}
                shimmering={shimmerKey === k}
              />
            ))}
          </div>
        )}

        {!generating && shownKeys.length === 0 && (
          <div className="preview-empty">
            <div className="ill"><Sparkle size={40} style={{ color: "var(--ai)" }} /></div>
            <div>
              <div style={{ fontWeight: 600, color: "var(--ink)", marginBottom: 4 }}>No previews yet</div>
              <div>
                Pick your platforms, then hit <strong>Generate</strong> to watch one idea become{" "}
                {postCount || "several"} native posts.
              </div>
            </div>
          </div>
        )}
      </div>

      {/* ACTION BAR */}
      <div className="action-bar">
        <div className="action-summary">
          Posting to <strong>{postCount}</strong> platform{postCount === 1 ? "" : "s"}
        </div>
        <span className="spacer" />
        <button className="btn btn-ghost" onClick={saveDraft}>Save draft</button>
        <button className="btn btn-spark" onClick={() => setModal("post")} disabled={!canPublish}>
          <Icon name="send" size={17} /> Post now
        </button>
      </div>

      {modal && (
        <ConfirmModal
          mode={modal}
          platforms={shownKeys as PlatformKey[]}
          onClose={() => setModal(null)}
          onConfirm={confirmAction}
        />
      )}
    </div>
  );
}
