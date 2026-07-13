# tests/test_bitrix24_sending.py
import asyncio
import importlib.util
import os
import sys
import pytest
from unittest.mock import MagicMock

# Load base module
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

# Load adapter module
_adapter_path = os.path.join(
    os.path.dirname(__file__), "..", "gateway", "platforms", "bitrix24", "adapter.py"
)
_spec = importlib.util.spec_from_file_location("gateway.platforms.bitrix24.adapter", os.path.abspath(_adapter_path))
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
Bitrix24Adapter = _mod.Bitrix24Adapter


@pytest.fixture
def mock_config():
    config = MagicMock()
    config.extra = {
        "api_key": "test_key",
        "base_url": "https://test.api",
        "bot_id": 123,
    }
    return config


@pytest.fixture
def adapter(mock_config):
    return Bitrix24Adapter(mock_config)


def test_send_message(adapter):
    mock_client = MagicMock()
    mock_client.send_message.return_value = {"success": True}
    adapter._client = mock_client

    result = asyncio.run(adapter.send("bitrix24:12345", "Hello!"))

    assert result.success is True
    mock_client.send_message.assert_called_once_with(123, "12345", "Hello!")


def test_send_message_no_colon(adapter):
    mock_client = MagicMock()
    mock_client.send_message.return_value = {"success": True}
    adapter._client = mock_client

    result = asyncio.run(adapter.send("12345", "Hello!"))

    assert result.success is True
    mock_client.send_message.assert_called_once_with(123, "12345", "Hello!")


def test_send_message_failure(adapter):
    mock_client = MagicMock()
    mock_client.send_message.return_value = None
    adapter._client = mock_client

    result = asyncio.run(adapter.send("bitrix24:12345", "Hello!"))

    assert result.success is False
    assert result.error == "No response from Bitrix24 API"


def test_send_message_exception(adapter):
    mock_client = MagicMock()
    mock_client.send_message.side_effect = RuntimeError("Connection failed")
    adapter._client = mock_client

    result = asyncio.run(adapter.send("bitrix24:12345", "Hello!"))

    assert result.success is False
    assert result.error == "Connection failed"
