"""Bitrix24 platform adapter for Hermes Agent."""
import asyncio
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Lazy imports to avoid circular dependencies at module level
_BasePlatformAdapter = None
_MessageEvent = None
_MessageType = None
_SendResult = None
_Bitrix24Client = None


def _load_deps():
    global _BasePlatformAdapter, _MessageEvent, _MessageType, _SendResult, _Bitrix24Client
    if _BasePlatformAdapter is not None:
        return

    from gateway.platforms.base import (
        BasePlatformAdapter,
        MessageEvent,
        MessageType,
        SendResult,
    )
    _BasePlatformAdapter = BasePlatformAdapter
    _MessageEvent = MessageEvent
    _MessageType = MessageType
    _SendResult = SendResult

    try:
        from gateway.platforms.bitrix24.client import Bitrix24Client
    except ImportError:
        import importlib.util
        import os
        _client_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "..",
            "gateway", "platforms", "bitrix24", "client.py",
        )
        _spec = importlib.util.spec_from_file_location(
            "bitrix24_client", os.path.abspath(_client_path)
        )
        _mod = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_mod)
        Bitrix24Client = _mod.Bitrix24Client

    _Bitrix24Client = Bitrix24Client


class Bitrix24Adapter:
    """Bitrix24 adapter implementing the Hermes platform interface."""

    def __init__(self, config):
        _load_deps()
        from gateway.config import Platform
        self._config = config
        self._platform = Platform.BITRIX24
        self._api_key = config.extra.get("api_key", "")
        self._base_url = config.extra.get(
            "base_url", "https://vibecode.bitrix24.tech/v1"
        )
        self._poll_interval = int(config.extra.get("poll_interval", 3))
        self._bot_id = config.extra.get("bot_id")
        self._offset = None
        self._connected = False
        self._client = _Bitrix24Client(self._api_key, self._base_url)
        self._on_message = None

    def _mark_connected(self):
        self._connected = True

    def _mark_disconnected(self):
        self._connected = False

    async def connect(self, *, is_reconnect: bool = False) -> bool:
        self._mark_connected()
        return True

    async def disconnect(self) -> None:
        self._mark_disconnected()

    def on_message(self, callback):
        """Register message handler."""
        self._on_message = callback

    async def send(
        self,
        chat_id: str,
        content: str,
        reply_to: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        _load_deps()
        if ":" in chat_id:
            dialog_id = chat_id.split(":", 1)[1]
        else:
            dialog_id = chat_id

        try:
            result = self._client.send_message(self._bot_id, dialog_id, content)
            if result is not None:
                logger.info("[bitrix24] Message sent to dialog %s", dialog_id)
                return _SendResult(success=True)
            else:
                logger.error(
                    "[bitrix24] Failed to send message to dialog %s: no response",
                    dialog_id,
                )
                return _SendResult(success=False, error="No response from Bitrix24 API")
        except Exception as e:
            logger.error("[bitrix24] Error sending message to dialog %s: %s", dialog_id, e)
            return _SendResult(success=False, error=str(e))

    async def poll_messages(self) -> None:
        while self._connected:
            try:
                response = self._client.get_events(self._bot_id, self._offset)
                if response and "events" in response:
                    for event in response["events"]:
                        await self._handle_event(event)
                    if "nextOffset" in response:
                        self._offset = response["nextOffset"]
                elif response and "nextOffset" in response:
                    self._offset = response["nextOffset"]
            except Exception as e:
                logger.error("[bitrix24] Error polling messages: %s", e)
            await asyncio.sleep(self._poll_interval)

    async def _handle_event(self, event: Dict[str, Any]) -> None:
        if event.get("event") != "ONIMBOTV2MESSAGEADD":
            return
        params = event.get("params", {})
        if params.get("system") or params.get("from_bot"):
            return

        _load_deps()
        message_event = _MessageEvent(
            chat_id=params.get("chat_id", ""),
            user_id=params.get("user_id", ""),
            text=params.get("message", ""),
            message_type=_MessageType.USER,
            raw=event,
        )
        if self._on_message:
            await self._on_message(message_event)
