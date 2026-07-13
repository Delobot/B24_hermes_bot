"""Bitrix24 platform plugin for Hermes Agent."""
import logging
from .adapter import Bitrix24Adapter

logger = logging.getLogger(__name__)


def check_requirements():
    """Check if plugin requirements are met."""
    import os
    return bool(os.environ.get("VIBE_API_KEY"))


def _env_enablement():
    """Auto-populate PlatformConfig.extra from env."""
    import os
    api_key = os.getenv("VIBE_API_KEY", "").strip()
    if not api_key:
        return None
    return {
        "api_key": api_key,
        "bot_id": int(os.getenv("BOT_ID", "19")),
        "base_url": os.getenv("VIBE_API_URL", "https://vibecode.bitrix24.tech/v1"),
        "poll_interval": int(os.getenv("POLL_INTERVAL", "3")),
    }


def register(ctx):
    """Register Bitrix24 platform with Hermes."""
    ctx.register_platform(
        name="bitrix24",
        label="Bitrix24",
        adapter_factory=lambda cfg: Bitrix24Adapter(cfg),
        check_fn=check_requirements,
        required_env=["VIBE_API_KEY"],
        env_enablement_fn=_env_enablement,
        emoji="💬",
        platform_hint="You are chatting via Bitrix24. Keep responses concise.",
    )
    logger.info("[bitrix24] Plugin registered")
