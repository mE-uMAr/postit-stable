/* ============================================================
   Postit — per-platform rewrite engine (heuristic, no real AI)
   ============================================================ */

import type { PlatformKey } from "./types";

export function hashtagsFrom(text: string): string[] {
  const stop = new Set([
    "this", "that", "with", "your", "from", "about", "into", "just",
    "here", "live", "now", "our", "the", "and", "for", "are", "out",
  ]);
  const words = (text.toLowerCase().match(/[a-z]{4,}/g) || []).filter((w) => !stop.has(w));
  const uniq = [...new Set(words)].slice(0, 3);
  return uniq.map((w) => "#" + w.charAt(0).toUpperCase() + w.slice(1));
}

export function firstSentence(t: string): string {
  return (t.split(/[.!?\n]/)[0] || t).trim();
}

export function rewriteFor(key: PlatformKey, text: string, tone: string): string {
  const t = text.trim();
  if (!t) return "";
  const tags = hashtagsFrom(t);
  const lead = firstSentence(t);
  switch (key) {
    case "x":
      return `${t}${tags.length ? "\n\n" + tags.join(" ") : ""}`.slice(0, 270);
    case "linkedin":
      return `${tone === "Bold" ? "Big news. " : "We're excited to share — "}${t}\n\nWe'd love to hear what you think. 👇`;
    case "instagram":
      return `${t.toLowerCase()}\n\n✨ tap the link in bio to see more →${tags.length ? "\n" + tags.map((x) => x.toLowerCase()).join(" ") : ""}`;
    case "threads":
      return `${t} 🌷\n\nwhich one are you most into?`;
    case "facebook":
      return `${t}\n\nDrop a comment and let us know what you think! 💬`;
    case "tiktok":
      return `${lead.toLowerCase()} 🎬\n\n${tags.map((x) => x.toLowerCase()).join(" ")}`;
    case "youtube":
      return `${lead}\n\nWatch the full story in this short. Subscribe for more. ${tags.join(" ")}`;
    case "wordpress":
    case "blogger":
      return `${lead}: what you need to know\n\n${t}\n\nRead the full post on our blog for the complete details and behind-the-scenes.`;
    default:
      return t;
  }
}

export function titleFor(t: string): string {
  return firstSentence(t).slice(0, 48) || "Untitled draft";
}
