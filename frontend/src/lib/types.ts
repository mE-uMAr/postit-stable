/* ============================================================
   Postit — shared domain types
   ============================================================ */

export type PlatformKey =
  | "x"
  | "linkedin"
  | "instagram"
  | "threads"
  | "facebook"
  | "tiktok"
  | "youtube"
  | "wordpress"
  | "blogger";

export interface Platform {
  key: PlatformKey;
  name: string;
  /** CSS class carrying the brand color, e.g. "pf-x" */
  cls: string;
  /** Monogram shown in the platform mark */
  glyph: string;
  handle: string;
  author: string;
  /** Character ceiling, if the platform enforces one */
  limit?: number;
  needsMedia?: boolean;
  needsVideo?: boolean;
  longform?: boolean;
}

export interface Eligibility {
  ok: boolean;
  reason?: string;
  warn?: string;
}

export interface EligibilityInput {
  hasMedia: boolean;
  hasVideo: boolean;
  charCount: number;
}
