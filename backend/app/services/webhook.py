"""Send webhook notifications when a campaign pipeline completes."""

import logging
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


async def notify_campaign_complete(
    title: str,
    viral_score: float | None,
    summary: str | None,
    campaign_id: str,
) -> None:
    """Send webhook notifications to configured Slack/Discord channels."""
    score = int(viral_score) if viral_score is not None else "N/A"
    short_summary = (summary or "No summary")[:200]

    if settings.webhook_slack:
        await _send_slack(title, score, short_summary, campaign_id)

    if settings.webhook_discord:
        await _send_discord(title, score, short_summary, campaign_id)


async def _send_slack(title: str, score, summary: str, campaign_id: str) -> None:
    text = f"*Campaign completed:* {title}\n*Viral Score:* {score}/100\n{summary}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.post(settings.webhook_slack, json={"text": text})
    except Exception as e:
        logger.warning("Slack webhook failed: %s", e)


async def _send_discord(title: str, score, summary: str, campaign_id: str) -> None:
    embed = {
        "title": f"Campaign: {title}",
        "description": summary,
        "color": 0x00FF00 if isinstance(score, int) and score >= 60 else 0xFF6600,
        "fields": [{"name": "Viral Score", "value": f"{score}/100", "inline": True}],
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.post(settings.webhook_discord, json={"embeds": [embed]})
    except Exception as e:
        logger.warning("Discord webhook failed: %s", e)
