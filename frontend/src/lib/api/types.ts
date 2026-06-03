/* TypeScript shapes mirroring the backend Pydantic read schemas. */

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

export interface ApiUser {
  id: string;
  email: string;
  full_name: string;
  avatar_url: string | null;
  is_active: boolean;
  is_superuser: boolean;
  is_verified: boolean;
  last_login_at: string | null;
  created_at: string;
}

export interface ApiWorkspace {
  id: string;
  name: string;
  slug: string;
  logo_text: string;
  owner_id: string;
  settings: Record<string, unknown>;
  created_at: string;
  role?: string;
}

export interface ApiPlatform {
  id: string;
  name: string;
  color: string;
  requires_media: boolean;
  requires_video: boolean;
  char_limit: number | null;
  supports_longform: boolean;
  is_active: boolean;
  sort_order: number;
}

export type ConnectionStatus = "connected" | "expired" | "disconnected" | "revoked";

export interface ApiConnection {
  id: string;
  workspace_id: string;
  platform_id: string;
  handle: string | null;
  display_name: string | null;
  avatar_text: string | null;
  status: ConnectionStatus;
  token_expires_at: string | null;
  created_at: string;
}

export type PostStatus =
  | "draft"
  | "generating"
  | "ready"
  | "scheduled"
  | "publishing"
  | "published"
  | "partially_failed"
  | "failed";

export type TargetStatus =
  | "pending"
  | "scheduled"
  | "publishing"
  | "published"
  | "failed"
  | "skipped";

export interface ApiTarget {
  id: string;
  post_id: string;
  platform_id: string;
  connection_id: string | null;
  content: string;
  edited: boolean;
  status: TargetStatus;
  external_post_id: string | null;
  error: string | null;
  published_at: string | null;
}

export interface ApiPost {
  id: string;
  workspace_id: string;
  author_id: string | null;
  title: string;
  body: string;
  tone: string;
  media: { type: string; id?: string }[];
  status: PostStatus;
  scheduled_at: string | null;
  published_at: string | null;
  created_at: string;
  updated_at: string;
  targets: ApiTarget[];
}

export interface Paginated<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface ApiPlan {
  id: string;
  code: string;
  name: string;
  description: string | null;
  price_monthly_cents: number;
  price_annual_cents: number;
  currency: string;
  annual_discount_percent: number;
  max_connections: number;
  max_ai_posts_monthly: number;
  max_seats: number;
  features: string[];
  is_active: boolean;
  is_public: boolean;
  sort_order: number;
}

export interface ApiSubscription {
  id: string;
  workspace_id: string;
  plan_id: string;
  status: string;
  billing_cycle: "monthly" | "annual";
  current_period_end: string | null;
  cancel_at_period_end: boolean;
  plan: ApiPlan;
}

export interface ApiUsage {
  period: string;
  ai_posts_used: number;
  ai_posts_limit: number;
  posts_published: number;
  connections_used: number;
  connections_limit: number;
  seats_used: number;
  seats_limit: number;
}

export interface ApiMember {
  id: string;
  role: string;
  status: string;
  name: string;
  email: string;
  avatar: string;
}

export interface ApiBrandVoice {
  tone: string;
  guidelines: string | null;
  words_to_avoid: string[];
}

export interface ApiNotificationPrefs {
  published: boolean;
  failed: boolean;
  weekly: boolean;
  suggestions: boolean;
}

export interface MetricDelta {
  value: string;
  label: string;
  direction: string;
}

export interface ApiAnalytics {
  range_days: number;
  overview: {
    total_reach: number;
    engagement_rate: number;
    posts_published: number;
    reach_delta: MetricDelta;
    engagement_delta: MetricDelta;
    posts_delta: MetricDelta;
  };
  trend: { label: string; date: string; value: number }[];
  by_platform: { platform_id: string; name: string; color: string; value: number; percent: number }[];
}

/* ---- Admin ---- */
export interface AdminMetrics {
  total_users: number;
  active_users: number;
  new_users_30d: number;
  total_workspaces: number;
  active_workspaces: number;
  total_posts: number;
  posts_published: number;
  paying_subscriptions: number;
  mrr_cents: number;
  arr_cents: number;
  plan_distribution: Record<string, number>;
}

export interface AdminUser extends ApiUser {
  workspace_count: number;
}

export interface AdminWorkspace {
  id: string;
  name: string;
  slug: string;
  owner_id: string;
  created_at: string;
  member_count: number;
  post_count: number;
  plan_name: string | null;
}

export interface AdminSubscription {
  id: string;
  workspace_id: string;
  workspace_name: string;
  plan_name: string;
  status: string;
  billing_cycle: string;
  mrr_cents: number;
  current_period_end: string | null;
}

export interface AdminAuditLog {
  id: string;
  actor_id: string | null;
  workspace_id: string | null;
  action: string;
  target_type: string | null;
  target_id: string | null;
  meta: Record<string, unknown> | null;
  ip: string | null;
  created_at: string;
}
