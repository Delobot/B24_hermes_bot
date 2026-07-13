# tests/test_bitrix24_polling.py
import importlib.util
import os
import sys
import pytest
from unittest.mock import MagicMock

# First, load the base module to make it available for import
_base_path = os.path.join(
    os.path.dirname(__file__), "..", "gateway", "platforms", "base.py"
)
_base_spec = importlib.util.spec_from_file_location("gateway.platforms.base", os.path.abspath(_base_path))
_base_mod = importlib.util.module_from_spec(_base_spec)
sys.modules["gateway.platforms.base"] = _base_mod
_base_spec.loader.exec_module(_base_mod)

# Load config module
_config_path = os.path.join(
    os.path.dirname(__file__), "..", "gateway", "config.py"
)
_config_spec = importlib.util.spec_from_file_location("gateway.config", os.path.abspath(_config_path))
_config_mod = importlib.util.module_from_spec(_config_spec)
sys.modules["gateway.config"] = _config_mod
_config_spec.loader.exec_module(_config_mod)

# Load client module
_client_path = os.path.join(
    os.path.dirname(__file__), "..", "gateway", "platforms", "bitrix24", "client.py"
)
_client_spec = importlib.util.spec_from_file_location("gateway.platforms.bitrix24.client", os.path.abspath(_client_path))
_client_mod = importlib.util.module_from_spec(_client_spec)
sys.modules["gateway.platforms.bitrix24.client"] = _client_mod
_client_spec.loader.exec_module(_client_mod)

# Now load the adapter module
_adapter_path = os.path.join(
    os.path.dirname(__file__), "..", "gateway", "platforms", "bitrix24", "adapter.py"
)
_spec = importlib.util.spec_from_file_location("gateway.platforms.bitrix24.adapter", os.path.abspath(_adapter_path))
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
Bitrix24Adapter = _mod.Bitrix24Adapter


def test_adapter_initialization():
    config = MagicMock()
    config.extra = {"api_key": "test", "base_url": "https://test", "bot_id": 123}
    adapter = Bitrix24Adapter(config)
    assert adapter._bot_id == 123
    assert adapter._api_key == "test"
    assert adapter._poll_interval == 3


def test_adapter_has_poll_method():
    config = MagicMock()
    config.extra = {"api_key": "test", "base_url": "https://test", "bot_id": 123}
    adapter = Bitrix24Adapter(config)
    assert hasattr(adapter, 'poll_messages')
    assert callable(adapter.poll_messages)


def test_adapter_has_handle_event_method():
    config = MagicMock()
    config.extra = {"api_key": "test", "base_url": "https://test", "bot_id": 123}
    adapter = Bitrix24Adapter(config)
    assert hasattr(adapter, '_handle_event')
    assert callable(adapter._handle_event)


def test_adapter_initializes_client():
    config = MagicMock()
    config.extra = {"api_key": "test", "base_url": "https://test", "bot_id": 123}
    adapter = Bitrix24Adapter(config)
    assert adapter._client is not None
