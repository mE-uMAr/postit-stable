/* ============================================================
   Postit - platform catalog + eligibility rules
   ============================================================ */

import type { Eligibility, EligibilityInput, Platform, PlatformKey } from "./types";

export const PLATFORMS: Platform[] = [
  { key: "x", name: "X", cls: "pf-x", glyph: "X", handle: "@maplehome", author: "Maple & Co", limit: 280 },
  { key: "linkedin", name: "LinkedIn", cls: "pf-linkedin", glyph: "in", handle: "Home goods · 1d", author: "Maple & Co", limit: 3000 },
  { key: "instagram", name: "Instagram", cls: "pf-instagram", glyph: "Ig", handle: "Original audio", author: "maple.home", needsMedia: true },
  { key: "threads", name: "Threads", cls: "pf-threads", glyph: "@", handle: "2m", author: "maple.home", limit: 500 },
  { key: "facebook", name: "Facebook", cls: "pf-facebook", glyph: "f", handle: "· 3m", author: "Maple & Co" },
  { key: "tiktok", name: "TikTok", cls: "pf-tiktok", glyph: "t", handle: "maple.home", author: "maple.home", needsVideo: true },
  { key: "youtube", name: "YouTube", cls: "pf-youtube", glyph: "▶", handle: "Maple & Co", author: "Maple & Co", needsVideo: true },
  { key: "wordpress", name: "WordPress", cls: "pf-wordpress", glyph: "W", handle: "maple.blog", author: "Maple & Co", longform: true },
  { key: "blogger", name: "Blogger", cls: "pf-blogger", glyph: "B", handle: "maple.blogspot", author: "Maple & Co", longform: true },
];

/** Quick lookup by key. */
export const PF: Record<PlatformKey, Platform> = Object.fromEntries(
  PLATFORMS.map((p) => [p.key, p]),
) as Record<PlatformKey, Platform>;

export function eligibility(p: Platform, { hasMedia, hasVideo, charCount }: EligibilityInput): Eligibility {
  if (p.needsVideo && !hasVideo) return { ok: false, reason: "Needs a video - disabled for this post." };
  if (p.needsMedia && !hasMedia) return { ok: false, reason: "Instagram requires an image or video." };
  if (p.limit && charCount > p.limit) return { ok: true, warn: `Over ${p.limit} characters - Postit will trim.` };
  return { ok: true };
}
