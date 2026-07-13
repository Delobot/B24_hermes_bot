# B24 Hermes Bot — Bitrix24 Platform Plugin

This project provides a **Bitrix24 platform adapter** for the Hermes Agent
framework, packaged as a Hermes Platform Plugin.

## Directory Structure

```
B24_hermes_bot/
├── plugins/
│   └── platforms/
│       └── bitrix24/
│           ├── __init__.py      # register(ctx) — plugin entry point
│           ├── adapter.py       # Bitrix24Adapter(BasePlatformAdapter)
│           └── plugin.yaml      # Plugin manifest
├── gateway/
│   └── platforms/
│       └── bitrix24/
│           ├── __init__.py      # Deprecated — re-exports from plugins/
│           ├── adapter.py       # Original adapter (kept for reference)
│           └── client.py        # Bitrix24Client HTTP helper
├── config/
├── tests/
└── README.md
```

## Plugin Architecture

The new structure follows the Hermes Platform Plugin convention:

| File | Purpose |
|------|---------|
| `plugins/platforms/bitrix24/__init__.py` | Exposes `register(ctx)` — called by the Hermes plugin loader to register the platform |
| `plugins/platforms/bitrix24/adapter.py` | `Bitrix24Adapter` class — implements connect/disconnect/send/poll |
| `plugins/platforms/bitrix24/plugin.yaml` | Declarative manifest (name, version, required env vars) |

### Registration

The `register(ctx)` function calls `ctx.register_platform()` with:

- `adapter_factory` — creates a `Bitrix24Adapter` from a `PlatformConfig`
- `check_fn` — verifies `VIBE_API_KEY` is set
- `env_enablement_fn` — auto-populates config from environment variables

### Required Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VIBE_API_KEY` | VibeCode API key (`vibe_api_...`) | *(required)* |
| `BOT_ID` | Bitrix24 bot ID | `19` |
| `VIBE_API_URL` | VibeCode API base URL | `https://vibecode.bitrix24.tech/v1` |
| `POLL_INTERVAL` | Message poll interval (seconds) | `3` |

## Backward Compatibility

The old `gateway/platforms/bitrix24/__init__.py` still re-exports
`Bitrix24Adapter` but emits a `DeprecationWarning`. Update imports to:

```python
from plugins.platforms.bitrix24 import Bitrix24Adapter
# or
from plugins.platforms.bitrix24.adapter import Bitrix24Adapter
```

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/

# Set env vars
export VIBE_API_KEY="vibe_api_..."
export BOT_ID=19
```
