"""Domain enumerations (stored as portable VARCHARs)."""

from __future__ import annotations

from enum import StrEnum


class WorkspaceRole(StrEnum):
    owner = "owner"
    admin = "admin"
    editor = "editor"
    viewer = "viewer"


# Role hierarchy for `require_workspace_role`.
ROLE_RANK: dict[str, int] = {
    WorkspaceRole.viewer: 1,
    WorkspaceRole.editor: 2,
    WorkspaceRole.admin: 3,
    WorkspaceRole.owner: 4,
}


class MembershipStatus(StrEnum):
    active = "active"
    invited = "invited"
    suspended = "suspended"


class AuthProvider(StrEnum):
    local = "local"
    google = "google"
    apple = "apple"


class ConnectionStatus(StrEnum):
    connected = "connected"
    expired = "expired"
    disconnected = "disconnected"
    revoked = "revoked"


class PostStatus(StrEnum):
    draft = "draft"
    generating = "generating"
    ready = "ready"
    scheduled = "scheduled"
    publishing = "publishing"
    published = "published"
    partially_failed = "partially_failed"
    failed = "failed"


class TargetStatus(StrEnum):
    pending = "pending"
    scheduled = "scheduled"
    publishing = "publishing"
    published = "published"
    failed = "failed"
    skipped = "skipped"


class BillingCycle(StrEnum):
    monthly = "monthly"
    annual = "annual"


class SubscriptionStatus(StrEnum):
    trialing = "trialing"
    active = "active"
    past_due = "past_due"
    canceled = "canceled"
    incomplete = "incomplete"


class InvoiceStatus(StrEnum):
    draft = "draft"
    open = "open"
    paid = "paid"
    void = "void"
    uncollectible = "uncollectible"


class NotificationType(StrEnum):
    post_published = "post_published"
    post_failed = "post_failed"
    weekly_digest = "weekly_digest"
    ai_suggestion = "ai_suggestion"
    system = "system"


class PublishJobStatus(StrEnum):
    pending = "pending"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"
