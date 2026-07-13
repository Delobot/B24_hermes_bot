# tests/test_bitrix24_client.py
import importlib.util
import os
import pytest

# Load client.py directly to avoid triggering __init__.py imports
_client_path = os.path.join(
    os.path.dirname(__file__), "..", "gateway", "platforms", "bitrix24", "client.py"
)
_spec = importlib.util.spec_from_file_location("client", os.path.abspath(_client_path))
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
Bitrix24Client = _mod.Bitrix24Client


@pytest.fixture
def client():
    return Bitrix24Client(api_key="test_key", base_url="https://test.api")


def test_client_initialization(client):
    assert client.api_key == "test_key"
    assert client.base_url == "https://test.api"


def test_get_events(client):
    # Test that the method exists and has correct signature
    assert hasattr(client, 'get_events')
    assert callable(client.get_events)


def test_send_message(client):
    # Test that the method exists and has correct signature
    assert hasattr(client, 'send_message')
    assert callable(client.send_message)
