"""Per-platform rewrite engine (heuristic; ported from the frontend lib).

Deterministic, no external model call - the backend is the source of truth for
generation so the frontend can drop its local copy.
"""

from __future__ import annotations

import re

_STOP = {
    "this", "that", "with", "your", "from", "about", "into", "just",
    "here", "live", "now", "our", "the", "and", "for", "are", "out",
}


def hashtags_from(text: str) -> list[str]:
    words = [w for w in re.findall(r"[a-z]{4,}", text.lower()) if w not in _STOP]
    uniq: list[str] = []
    for w in words:
        if w not in uniq:
            uniq.append(w)
        if len(uniq) == 3:
            break
    return ["#" + w[0].upper() + w[1:] for w in uniq]


def first_sentence(t: str) -> str:
    return re.split(r"[.!?\n]", t, maxsplit=1)[0].strip() or t.strip()


def title_for(t: str) -> str:
    return first_sentence(t)[:48] or "Untitled draft"


def rewrite_for(platform_id: str, text: str, tone: str) -> str:
    t = text.strip()
    if not t:
        return ""
    tags = hashtags_from(t)
    lead = first_sentence(t)

    if platform_id == "x":
        suffix = ("\n\n" + " ".join(tags)) if tags else ""
        return (t + suffix)[:270]
    if platform_id == "linkedin":
        opener = "Big news. " if tone == "Bold" else "We're excited to share - "
        return f"{opener}{t}\n\nWe'd love to hear what you think. 👇"
    if platform_id == "instagram":
        tagline = ("\n" + " ".join(x.lower() for x in tags)) if tags else ""
        return f"{t.lower()}\n\n✨ tap the link in bio to see more →{tagline}"
    if platform_id == "threads":
        return f"{t} 🌷\n\nwhich one are you most into?"
    if platform_id == "facebook":
        return f"{t}\n\nDrop a comment and let us know what you think! 💬"
    if platform_id == "tiktok":
        return f"{lead.lower()} 🎬\n\n{' '.join(x.lower() for x in tags)}"
    if platform_id == "youtube":
        return f"{lead}\n\nWatch the full story in this short. Subscribe for more. {' '.join(tags)}"
    if platform_id in ("wordpress", "blogger"):
        return (
            f"{lead}: what you need to know\n\n{t}\n\n"
            "Read the full post on our blog for the complete details and behind-the-scenes."
        )
    return t
