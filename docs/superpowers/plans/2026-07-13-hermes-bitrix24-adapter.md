# Hermes Bitrix24 Adapter Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create a native Bitrix24 platform adapter for Hermes Agent that enables bi-directional messaging between Bitrix24 chat and Hermes AI assistant.

**Architecture:** Extend Hermes gateway with a new `Bitrix24Adapter` class that polls Bitrix24 for incoming messages via VibeCode API, processes them through Hermes AI agent, and sends responses back to Bitrix24 chat.

**Tech Stack:** Python 3.13+, aiohttp, Hermes gateway framework, VibeCode API

## Global Constraints

- Python 3.11+ (Hermes requirement)
- Follow Hermes adapter pattern (BasePlatformAdapter)
- Use VibeCode API for Bitrix24 communication
- TDD approach: tests first, then implementation
- DRY, YAGNI principles
- Frequent commits after each task

---

## File Structure

```
B24_hermes_bot/
├── gateway/
│   └── platforms/
│       └── bitrix24/
│           ├── __init__.py          # Package init
│           └── adapter.py           # Bitrix24Adapter class
├── tests/
│   └── test_bitrix24_adapter.py    # Unit tests
├── docs/
│   └── superpowers/
│       └── plans/
│           └── 2026-07-13-hermes-bitrix24-adapter.md  # This file
├── config/
│   └── bitrix24_example.yaml       # Example configuration
└── README.md                       # Documentation
```

---

### Task 1: Create Package Structure

**Files:**
- Create: `gateway/platforms/bitrix24/__init__.py`
- Create: `gateway/platforms/bitrix24/adapter.py` (skeleton)

**Interfaces:**
- Consumes: None (initial setup)
- Produces: `Bitrix24Adapter` class skeleton

- [ ] **Step 1: Create package directory**
```bash
mkdir -p gateway/platforms/bitrix24
```

- [ ] **Step 2: Create __init__.py**
```python
"""Bitrix24 platform adapter for Hermes Agent."""
from .adapter import Bitrix24Adapter
__all__ = ["Bitrix24Adapter"]
```

- [ ] **Step 3: Create adapter.py skeleton**
```python
"""Bitrix24 platform adapter for Hermes Agent."""
import asyncio
import logging
from typing import Any, Dict, Optional
from gateway.config import Platform, PlatformConfig
from gateway.platforms.base import (
    BasePlatformAdapter,
    MessageEvent,
    MessageType,
    SendResult,
)

logger = logging.getLogger(__name__)

class Bitrix24Adapter(BasePlatformAdapter):
    def __init__(self, config: PlatformConfig):
        super().__init__(config, Platform.BITRIX24)
        self._api_key = config.extra.get("api_key", "")
        self._base_url = config.extra.get("base_url", "https://vibecode.bitrix24.tech/v1")
        self._poll_interval = int(config.extra.get("poll_interval", 3))
        self._bot_id = config.extra.get("bot_id")
        self._offset = None

    async def connect(self, *, is_reconnect: bool = False) -> bool:
        self._mark_connected()
        return True

    async def disconnect(self) -> None:
        self._mark_disconnected()

    async def send(self, chat_id: str, content: str, reply_to: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> SendResult:
        return SendResult(success=True)

    async def poll_messages(self) -> None:
        pass
```

- [ ] **Step 4: Commit**
```bash
git add gateway/platforms/bitrix24/
git commit -m "feat(bitrix24): create package structure and adapter skeleton"
```

---

### Task 2: Implement API Client

**Files:**
- Create: `gateway/platforms/bitrix24/client.py`
- Create: `tests/test_bitrix24_client.py`

**Interfaces:**
- Consumes: VibeCode API endpoints
- Produces: `Bitrix24Client` class with API methods

- [ ] **Step 1: Write failing test**
```python
# tests/test_bitrix24_client.py
import pytest
from gateway.platforms.bitrix24.client import Bitrix24Client

@pytest.fixture
def client():
    return Bitrix24Client(api_key="test_key", base_url="https://test.api")

def test_client_initialization(client):
    assert client.api_key == "test_key"
```

- [ ] **Step 2: Run test (expect fail)**
```bash
pytest tests/test_bitrix24_client.py -v
```

- [ ] **Step 3: Implement client**
```python
# gateway/platforms/bitrix24/client.py
import json
import logging
from typing import Any, Dict, Optional
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)

class Bitrix24Client:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def _make_request(self, method: str, path: str, body: Optional[Dict] = None) -> Optional[Dict]:
        url = f"{self.base_url}{path}"
        headers = {"X-Api-Key": self.api_key, "Content-Type": "application/json"}
        data = json.dumps(body).encode() if body else None
        req = Request(url, data=data, headers=headers, method=method)
        try:
            with urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            logger.error("API error: %s", e)
            return None

    def get_events(self, bot_id: int, offset: Optional[int] = None) -> Optional[Dict]:
        path = f"/bots/{bot_id}/events"
        if offset: path += f"?offset={offset}"
        return self._make_request("GET", path)

    def send_message(self, bot_id: int, dialog_id: str, message: str) -> Optional[Dict]:
        return self._make_request("POST", f"/bots/{bot_id}/messages", {"dialogId": dialog_id, "fields": {"message": message}})
```

- [ ] **Step 4: Run test (expect pass)**
```bash
pytest tests/test_bitrix24_client.py -v
```

- [ ] **Step 5: Commit**
```bash
git add gateway/platforms/bitrix24/client.py tests/test_bitrix24_client.py
git commit -m "feat(bitrix24): implement API client"
```

---

### Task 3: Implement Message Polling

**Files:**
- Modify: `gateway/platforms/bitrix24/adapter.py`
- Create: `tests/test_bitrix24_polling.py`

**Interfaces:**
- Consumes: `Bitrix24Client`
- Produces: `poll_messages()` method

- [ ] **Step 1: Write test**
```python
# tests/test_bitrix24_polling.py
import pytest
from unittest.mock import MagicMock
from gateway.platforms.bitrix24.adapter import Bitrix24Adapter

def test_adapter_initialization():
    config = MagicMock()
    config.extra = {"api_key": "test", "base_url": "https://test", "bot_id": 123}
    adapter = Bitrix24Adapter(config)
    assert adapter._bot_id == 123
```

- [ ] **Step 2: Implement polling**
```python
# Add to adapter.py
async def poll_messages(self) -> None:
    from gateway.platforms.bitrix24.client import Bitrix24Client
    client = Bitrix24Client(self._api_key, self._base_url)
    while True:
        try:
            result = client.get_events(self._bot_id, self._offset)
            if result and result.get("success"):
                for event in result.get("data", {}).get("events", []):
                    await self._handle_event(event)
                if result["data"].get("nextOffset"):
                    self._offset = result["data"]["nextOffset"]
            await asyncio.sleep(self._poll_interval)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error("Poll error: %s", e)
            await asyncio.sleep(5)

async def _handle_event(self, event: Dict) -> None:
    if event.get("type") != "ONIMBOTV2MESSAGEADD":
        return
    data = event.get("data", {})
    msg = data.get("message", {})
    if msg.get("isSystem") or msg.get("authorId") == self._bot_id:
        return
    source = self.build_source(
        chat_id=f"bitrix24:{data.get('chat', {}).get('dialogId', '')}",
        chat_name="bitrix24",
        chat_type="dm",
        user_id=str(msg.get("authorId", "")),
        user_name=data.get("user", {}).get("firstName", "user"),
    )
    await self.handle_message(MessageEvent(text=msg.get("text", ""), message_type=MessageType.TEXT, source=source, raw_message=event))
```

- [ ] **Step 3: Commit**
```bash
git add gateway/platforms/bitrix24/adapter.py tests/test_bitrix24_polling.py
git commit -m "feat(bitrix24): implement message polling"
```

---

### Task 4: Implement Message Sending

**Files:**
- Modify: `gateway/platforms/bitrix24/adapter.py`
- Create: `tests/test_bitrix24_sending.py`

- [ ] **Step 1: Implement send**
```python
# Add to adapter.py
async def send(self, chat_id: str, content: str, reply_to=None, metadata=None) -> SendResult:
    from gateway.platforms.bitrix24.client import Bitrix24Client
    client = Bitrix24Client(self._api_key, self._base_url)
    dialog_id = chat_id.replace("bitrix24:", "")
    result = client.send_message(self._bot_id, dialog_id, content)
    if result and result.get("success"):
        return SendResult(success=True)
    return SendResult(success=False, error=result.get("error", "Failed") if result else "No response")
```

- [ ] **Step 2: Commit**
```bash
git commit -m "feat(bitrix24): implement message sending"
```

---

### Task 5: Add Configuration

**Files:**
- Create: `config/bitrix24_example.yaml`

```yaml
platforms:
  bitrix24:
    enabled: true
    extra:
      api_key: "vibe_api_YOUR_KEY_HERE"
      bot_id: 19
      base_url: "https://vibecode.bitrix24.tech/v1"
      poll_interval: 3
```

- [ ] **Step 1: Commit**
```bash
git commit -m "feat(bitrix24): add configuration example"
```

---

## Execution Handoff

Plan complete. Two execution options:

1. **Subagent-Driven (recommended)** - Fresh subagent per task
2. **Inline Execution** - Execute in this session

Which approach?
