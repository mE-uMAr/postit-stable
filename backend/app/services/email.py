"""Transactional email via SMTP (stdlib, run off the event loop).

Uses the standard library so no extra dependency is required. When SMTP isn't
configured the call is a no-op (and, outside production, the body is logged so
local signup still works without a mail server).
"""

from __future__ import annotations

import asyncio
import smtplib
from email.message import EmailMessage
from email.utils import formataddr

from app.core.config import settings
from app.core.logging import logger


def _send_sync(to: str, subject: str, text: str, html: str | None) -> None:
    msg = EmailMessage()
    msg["From"] = formataddr((settings.SMTP_FROM_NAME, settings.email_from))
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(text)
    if html:
        msg.add_alternative(html, subtype="html")

    if settings.SMTP_USE_SSL:
        server: smtplib.SMTP = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=20)
    else:
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=20)
    try:
        server.ehlo()
        if settings.SMTP_USE_TLS and not settings.SMTP_USE_SSL:
            server.starttls()
            server.ehlo()
        if settings.SMTP_USER:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD or "")
        server.send_message(msg)
    finally:
        server.quit()


async def send_email(*, to: str, subject: str, text: str, html: str | None = None) -> None:
    """Send an email. Raises on SMTP failure when configured."""
    if not settings.smtp_configured:
        logger.warning("SMTP not configured; email to %s not sent (subject=%r)", to, subject)
        if not settings.is_production:
            logger.info("[DEV EMAIL] to=%s | %s\n%s", to, subject, text)
        return
    await asyncio.to_thread(_send_sync, to, subject, text, html)
