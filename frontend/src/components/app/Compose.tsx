"use client";

import { useRef, useState } from "react";
import { Icon } from "@/components/Icon";
import { Sparkle } from "@/components/Sparkle";
import { PlatformLogo } from "@/components/PlatformLogo";
import { eligibility, PF, PLATFORMS } from "@/lib/platforms";
import { rewriteFor } from "@/lib/rewrite";
import { prefersReducedMotion } from "@/lib/motion";
import type { Platform, PlatformKey } from "@/lib/types";
import { useToast } from "./providers/ToastProvider";
import { ConfirmModal, type ConfirmMode } from "./ConfirmModal";

const TONES = ["Professional", "Casual", "Bold", "Match my brand"];
const STARTER =
  "Launching our spring collection — lighter materials and a brighter palette, available today.";

interface MediaItem {
  type: "image" | "video";
  id: number;
}

interface Variant {
  text: string;
  edited: boolean;
  hasMedia: boolean;
}

type Variants = Record<string, Variant>;

interface NativePreviewCardProps {
  p: Platform;
  variant: Variant;
  idx: number;
  onEdit: (key: PlatformKey, text: string) => void;
  onRegen: (key: PlatformKey) => void;
  shimmering: boolean;
}

function NativePreviewCard({ p, variant, idx, onEdit, onRegen, shimmering }: NativePreviewCardProps) {
  const ref = useRef<HTMLDivElement>(null);
  return (
    <div className={"npc in" + (shimmering ? " shimmering" : "")} style={{ animationDelay: idx * 60 + "ms" }}>
      <div className="npc-top">
        <div className="npc-av" style={{ background: `var(--${p.cls})` }}>
          <PlatformLogo platform={p.key} />
        </div>
        <div className="npc-id">
          <div className="nm">{p.author}</div>
          <div className="hd">{p.handle}</div>
        </div>
        <span className={"pf " + p.cls + " npc-pfbadge"} style={{ width: 24, height: 24, borderRadius: 7, fontSize: 11 }}>
          <PlatformLogo platform={p.key} />
        </span>
      </div>
      <div
        className="npc-body"
        contentEditable
        suppressContentEditableWarning
        ref={ref}
        onInput={() => {
          if (ref.current) onEdit(p.key, ref.current.innerText);
        }}
      >
        {variant.text}
      </div>
      {(p.needsMedia || p.needsVideo || variant.hasMedia) && (
        <div className="npc-media placeholder" style={{ borderRadius: 0 }}>
          {p.needsVideo ? "video frame" : "image"}
        </div>
      )}
      <div className="npc-actions">
        <span className="a">
          <Icon name="heart" size={16} /> 248
        </span>
        <span className="a">
          <Icon name="comment" size={16} /> 19
        </span>
        <span className="a">
          <Icon name="repost" size={16} /> 32
        </span>
        <span className="a" style={{ marginLeft: "auto" }}>
          <Icon name="send" size={16} />
        </span>
      </div>
      <div className="npc-foot">
        {variant.edited ? (
          <span className="edited">
            <Icon name="edit" size={13} /> Edited
          </span>
        ) : (
          <span className="edited" style={{ color: "var(--ai)" }}>
            <Sparkle size={13} /> AI generated
          </span>
        )}
        <button className="regen" onClick={() => onRegen(p.key)}>
          <Icon name="refresh" size={14} /> Regenerate
        </button>
      </div>
    </div>
  );
}

export function Compose() {
  const pushToast = useToast();

  const [text, setText] = useState(STARTER);
  const [tone, setTone] = useState("Match my brand");
  const [media, setMedia] = useState<MediaItem[]>([]);
  const [selected, setSelected] = useState<Set<PlatformKey>>(
    () => new Set<PlatformKey>(["x", "linkedin", "threads", "facebook"]),
  );
  const [variants, setVariants] = useState<Variants | null>(null);
  const [generating, setGenerating] = useState(false);
  const [shimmerKey, setShimmerKey] = useState<PlatformKey | null>(null);
  const [modal, setModal] = useState<ConfirmMode | null>(null);

  const hasMedia = media.length > 0;
  const hasVideo = media.some((m) => m.type === "video");
  const charCount = text.length;

  const elig = (key: PlatformKey) => eligibility(PF[key], { hasMedia, hasVideo, charCount });

  const toggle = (key: PlatformKey) => {
    if (!elig(key).ok) return;
    setSelected((s) => {
      const n = new Set(s);
      if (n.has(key)) n.delete(key);
      else n.add(key);
      return n;
    });
  };
  const selectAllEligible = () => {
    setSelected(new Set(PLATFORMS.filter((p) => elig(p.key).ok).map((p) => p.key)));
  };

  const addMedia = (type: MediaItem["type"]) =>
    setMedia((m) => [...m, { type, id: Date.now() + Math.random() }]);
  const removeMedia = (id: number) => setMedia((m) => m.filter((x) => x.id !== id));

  const eligibleSelected = [...selected].filter((k) => elig(k).ok);

  const generate = () => {
    if (!text.trim() || eligibleSelected.length === 0) return;
    setGenerating(true);
    setVariants(null);
    const delay = prefersReducedMotion() ? 0 : 1300;
    setTimeout(() => {
      const v: Variants = {};
      eligibleSelected.forEach((k) => {
        v[k] = { text: rewriteFor(k, text, tone), edited: false, hasMedia };
      });
      setVariants(v);
      setGenerating(false);
    }, delay);
  };

  const onEdit = (key: PlatformKey, newText: string) => {
    setVariants((v) => (v ? { ...v, [key]: { ...v[key], text: newText, edited: true } } : v));
  };
  const onRegen = (key: PlatformKey) => {
    setShimmerKey(key);
    setTimeout(
      () => {
        setVariants((v) => (v ? { ...v, [key]: { ...v[key], text: rewriteFor(key, text, tone), edited: false } } : v));
        setShimmerKey(null);
      },
      prefersReducedMotion() ? 0 : 900,
    );
  };

  // keep variants in sync when platforms get deselected
  const shownKeys: PlatformKey[] = variants
    ? (Object.keys(variants) as PlatformKey[]).filter((k) => selected.has(k) && elig(k).ok)
    : [];

  const xLimit = PF.x.limit ?? 280;
  const overX = selected.has("x") && charCount > xLimit;

  const summaryScheduled = 0;
  const postCount = eligibleSelected.length;

  return (
    <div className="compose-grid">
      {/* LEFT — composer + selector */}
      <div className="compose-left">
        <div className="composer-card">
          <div className="composer-toolbar">
            <button className="tool-btn" title="Bold">
              <Icon name="bold" size={18} />
            </button>
            <button className="tool-btn" title="Italic">
              <Icon name="italic" size={18} />
            </button>
            <button className="tool-btn" title="Link">
              <Icon name="link" size={18} />
            </button>
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
                <div key={m.id} className="media-thumb placeholder" style={{ fontSize: 10 }}>
                  {m.type === "video" ? "video" : "image"}
                  <button className="rm" onClick={() => removeMedia(m.id)}>
                    <Icon name="x" size={12} />
                  </button>
                </div>
              ))}
            </div>
          )}
          <div className="media-zone" onClick={() => addMedia("image")}>
            <Icon name="image" size={18} />
            <span>Drag images or video here, or click to add</span>
            <button
              className="btn btn-ghost btn-sm"
              style={{ marginLeft: 8 }}
              onClick={(e) => {
                e.stopPropagation();
                addMedia("video");
              }}
            >
              + Add video
            </button>
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
            <>
              <span className="spin" /> Generating…
            </>
          ) : (
            <>
              <Sparkle size={17} /> Generate platform versions
            </>
          )}
        </button>

        {/* platform selector */}
        <div className="psel">
          <div className="psel-head">
            <span className="ttl">Post to</span>
            <button className="all" onClick={selectAllEligible}>
              Select all eligible
            </button>
          </div>
          <div className="psel-grid">
            {PLATFORMS.map((p) => {
              const e = elig(p.key);
              const sel = selected.has(p.key);
              const warn = sel && e.warn;
              return (
                <button
                  key={p.key}
                  className={
                    "pchip" +
                    (sel ? " is-selected" : "") +
                    (!e.ok ? " is-disabled" : "") +
                    (warn ? " is-warning" : "")
                  }
                  onClick={() => toggle(p.key)}
                  title={e.reason || e.warn || ""}
                >
                  <span className={"pf-dot " + p.cls} />
                  {p.name}
                  {!e.ok && <Icon name="alert" size={14} style={{ marginLeft: 2, color: "var(--ink-faint)" }} />}
                  {warn && <Icon name="alert" size={14} style={{ marginLeft: 2, color: "var(--spark-deep)" }} />}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* RIGHT — preview grid */}
      <div className="compose-right">
        <div className="preview-head">
          <span className="ttl">
            Live preview · {shownKeys.length || postCount} platform
            {(shownKeys.length || postCount) === 1 ? "" : "s"}
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
                    <PlatformLogo platform={k} />
                  </div>
                  <div className="npc-id">
                    <div className="nm" style={{ color: "var(--ink-faint)" }}>
                      {PF[k].author}
                    </div>
                  </div>
                </div>
                <div className="npc-body" style={{ color: "var(--ink-faint)" }}>
                  Writing a native {PF[k].name} version…
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
                p={PF[k]}
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
            <div className="ill">
              <Sparkle size={40} style={{ color: "var(--ai)" }} />
            </div>
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
          {summaryScheduled > 0 && (
            <>
              {" "}
              · <strong>{summaryScheduled}</strong> scheduled
            </>
          )}
        </div>
        <span className="spacer" />
        <button className="btn btn-ghost" onClick={() => pushToast("Draft saved")}>
          Save draft
        </button>
        <button className="btn btn-secondary" onClick={() => setModal("schedule")}>
          <Icon name="clock" size={17} /> Schedule
        </button>
        <button className="btn btn-spark" onClick={() => setModal("post")} disabled={postCount === 0}>
          <Icon name="send" size={17} /> Post now
        </button>
      </div>

      {modal && (
        <ConfirmModal
          mode={modal}
          platforms={eligibleSelected}
          onClose={() => setModal(null)}
          onConfirm={() => {
            const count = postCount;
            const wasSchedule = modal === "schedule";
            setModal(null);
            pushToast(
              wasSchedule
                ? `Scheduled to ${count} platforms for 9:00 AM`
                : `Posted to ${count} platforms`,
            );
          }}
        />
      )}
    </div>
  );
}
