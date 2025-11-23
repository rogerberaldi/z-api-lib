"""
Pytest configuration and fixtures.

This module provides comprehensive fixtures for testing the zapi_async library.
Includes mocked clients, responses, and utilities for both unit and integration tests.
"""

import pytest
import asyncio
import json
import logging
from typing import AsyncGenerator, Dict, Any
from unittest.mock import Mock, AsyncMock, patch
import httpx

from zapi_async import ZAPIClient
from zapi_async.api import GraphAPI
from zapi_async.types import (
    SentMessage,
    InstanceStatus,
    TextMessage,
    ImageMessage,
)

# Configure logging for tests
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


# ============================================================
# EVENT LOOP FIXTURES
# ============================================================

@pytest.fixture(scope="session")
def event_loop():
    """
    Create event loop for async tests.
    
    Scope: session - one loop for all tests
    """
    logger.info("🔧 Setting up event loop for test session")
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    logger.info("🔧 Tearing down event loop")
    loop.close()


# ============================================================
# CONFIGURATION FIXTURES
# ============================================================

@pytest.fixture
def test_config() -> Dict[str, str]:
    """
    Test configuration with mock credentials.
    
    Returns:
        Dict with instance_id, token, and client_token
    """
    logger.debug("📝 Creating test configuration")
    return {
        "instance_id": "TEST_INSTANCE_123",
        "token": "TEST_TOKEN_ABC",
        "client_token": "TEST_CLIENT_TOKEN_XYZ"
    }


@pytest.fixture
def test_phone() -> str:
    """Test phone number."""
    return "5511999999999"


@pytest.fixture
def test_group_id() -> str:
    """Test group ID."""
    return "120363019502650977-group"


# ============================================================
# MOCK RESPONSE FIXTURES
# ============================================================

@pytest.fixture
def mock_sent_message_response() -> Dict[str, str]:
    """
    Mock successful message send response.
    
    Returns:
        Dict matching Z-API send response format
    """
    logger.debug("📦 Creating mock sent message response")
    return {
        "zaapId": "3999984263738042930CD6ECDE9VDWSA",
        "messageId": "D241XXXX732339502B68",
        "id": "D241XXXX732339502B68"
    }


@pytest.fixture
def mock_instance_status_connected() -> Dict[str, Any]:
    """Mock instance status - connected."""
    logger.debug("📦 Creating mock instance status (connected)")
    return {
        "connected": True,
        "status": "connected",
        "phone": "5511999999999"
    }


@pytest.fixture
def mock_instance_status_disconnected() -> Dict[str, Any]:
    """Mock instance status - disconnected."""
    logger.debug("📦 Creating mock instance status (disconnected)")
    return {
        "connected": False,
        "status": "disconnected",
        "phone": None
    }


@pytest.fixture
def mock_qrcode_response() -> Dict[str, str]:
    """Mock QR code response."""
    return {
        "value": "2@abc123def456",
        "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    }


@pytest.fixture
def mock_webhook_text_message() -> Dict[str, Any]:
    """
    Mock webhook payload for text message.
    
    Returns:
        Complete webhook payload matching Z-API format
    """
    logger.debug("📦 Creating mock webhook text message")
    return {
        "isStatusReply": False,
        "senderLid": "81896604192873@lid",
        "connectedPhone": "554499999999",
        "waitingMessage": False,
        "isEdit": False,
        "isGroup": False,
        "isNewsletter": False,
        "instanceId": "A20DA9C0183A2D35A260F53F5D2B9244",
        "messageId": "MSG123ABC",
        "phone": "5511999999999",
        "fromMe": False,
        "momment": 1632228638000,
        "status": "RECEIVED",
        "chatName": "Test User",
        "senderPhoto": "https://example.com/photo.jpg",
        "senderName": "Test User",
        "participantPhone": None,
        "participantLid": None,
        "photo": "https://example.com/photo.jpg",
        "broadcast": False,
        "type": "ReceivedCallback",
        "text": {
            "message": "Hello, this is a test message!"
        }
    }


@pytest.fixture
def mock_webhook_image_message() -> Dict[str, Any]:
    """Mock webhook payload for image message."""
    logger.debug("📦 Creating mock webhook image message")
    return {
        "isStatusReply": False,
        "instanceId": "A20DA9C0183A2D35A260F53F5D2B9244",
        "messageId": "IMG456DEF",
        "phone": "5511999999999",
        "fromMe": False,
        "momment": 1632228828000,
        "status": "RECEIVED",
        "chatName": "Test User",
        "senderName": "Test User",
        "isGroup": False,
        "isNewsletter": False,
        "type": "ReceivedCallback",
        "image": {
            "mimeType": "image/jpeg",
            "imageUrl": "https://example.com/image.jpg",
            "thumbnailUrl": "https://example.com/thumb.jpg",
            "caption": "Test image caption",
            "width": 1920,
            "height": 1080,
            "viewOnce": False
        }
    }


# ============================================================
# HTTP CLIENT FIXTURES
# ============================================================

@pytest.fixture
def mock_httpx_client():
    """
    Mock httpx.AsyncClient for testing HTTP requests.
    
    Returns:
        AsyncMock httpx client
    """
    logger.debug("🔧 Creating mock httpx client")
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    
    # Mock the request method
    async def mock_request(*args, **kwargs):
        logger.debug(f"📡 Mock HTTP request: {kwargs.get('method')} {kwargs.get('url')}")
        response = Mock(spec=httpx.Response)
        response.status_code = 200
        response.json.return_value = {
            "zaapId": "TEST_ZAAP_ID",
            "messageId": "TEST_MSG_ID",
            "id": "TEST_MSG_ID"
        }
        return response
    
    mock_client.request = mock_request
    mock_client.aclose = AsyncMock()
    
    return mock_client


@pytest.fixture
async def mock_graph_api(test_config, mock_httpx_client) -> AsyncGenerator[GraphAPI, None]:
    """
    Mock GraphAPI instance with mocked HTTP client.
    
    Args:
        test_config: Test configuration
        mock_httpx_client: Mocked httpx client
        
    Yields:
        GraphAPI instance with mocked session
    """
    logger.info("🏗️  Creating mock GraphAPI instance")
    api = GraphAPI(
        instance_id=test_config["instance_id"],
        token=test_config["token"],
        client_token=test_config["client_token"],
        session=mock_httpx_client
    )
    
    yield api
    
    logger.info("🧹 Cleaning up mock GraphAPI Instance")
    await api.close()


# ============================================================
# CLIENT FIXTURES
# ============================================================

@pytest.fixture
async def mock_client(test_config, mock_httpx_client) -> AsyncGenerator[ZAPIClient, None]:
    """
    Mock ZAPIClient with mocked HTTP session.
    
    This is the main fixture for testing client methods.
    All HTTP requests will be mocked.
    
    Args:
        test_config: Test configuration
        mock_httpx_client: Mocked httpx client
        
    Yields:
        ZAPIClient instance ready for testing
        
    Example:
        async def test_send_text(mock_client):
            result = await mock_client.send_text("5511999999999", "Test")
            assert result.message_id is not None
    """
    logger.info("🏗️  Creating mock ZAPIClient instance")
    client = ZAPIClient(
        instance_id=test_config["instance_id"],
        token=test_config["token"],
        client_token=test_config["client_token"],
        session=mock_httpx_client
    )
    
    yield client
    
    logger.info("🧹 Cleaning up mock ZAPIClient")
    await client.close()


@pytest.fixture
async def real_client(test_config) -> AsyncGenerator[ZAPIClient, None]:
    """
    Real ZAPIClient for integration tests.
    
    WARNING: This uses real HTTP requests. Only use for integration tests
    with actual Z-API credentials.
    
    Set environment variables:
        - ZAPI_INSTANCE_ID
        - ZAPI_TOKEN
        - ZAPI_CLIENT_TOKEN
        
    Yields:
        Real ZAPIClient instance
    """
    import os
    
    # Get credentials from environment
    instance_id = os.getenv("ZAPI_INSTANCE_ID", test_config["instance_id"])
    token = os.getenv("ZAPI_TOKEN", test_config["token"])
    client_token = os.getenv("ZAPI_CLIENT_TOKEN", test_config["client_token"])
    
    logger.warning("⚠️  Creating REAL ZAPIClient - will make actual HTTP requests!")
    logger.info(f"📱 Instance: {instance_id}")
    
    client = ZAPIClient(
        instance_id=instance_id,
        token=token,
        client_token=client_token
    )
    
    yield client
    
    logger.info("🧹 Cleaning up real ZAPIClient")
    await client.close()


# ============================================================
# PYTEST MARKERS
# ============================================================

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests (mocked, fast)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests (real API calls, slow)"
    )
    config.addinivalue_line(
        "markers", "webhook: Webhook parsing tests"
    )
    config.addinivalue_line(
        "markers", "slow: Slow tests (can be skipped)"
    )


# ============================================================
# HELPER FUNCTIONS FOR TESTS
# ============================================================

class MockHTTPResponse:
    """Helper class to create mock HTTP responses."""
    
    def __init__(self, status_code: int, json_data: Dict[str, Any]):
        self.status_code = status_code
        self._json_data = json_data
    
    def json(self):
        """Return JSON data."""
        return self._json_data
    
    def raise_for_status(self):
        """Mock raise for status."""
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                f"HTTP {self.status_code}",
                request=Mock(),
                response=self
            )


@pytest.fixture
def create_mock_response():
    """
    Factory fixture to create mock HTTP responses.
    
    Returns:
        Function that creates MockHTTPResponse
        
    Example:
        def test_something(create_mock_response):
            response = create_mock_response(200, {"success": True})
            assert response.status_code == 200
    """
    def _create(status_code: int, json_data: Dict[str, Any]) -> MockHTTPResponse:
        logger.debug(f"🏭 Creating mock response: {status_code}")
        return MockHTTPResponse(status_code, json_data)
    
    return _create


# ============================================================
# CAPLOG FIXTURE CONFIGURATION
# ============================================================

@pytest.fixture(autouse=True)
def configure_caplog(caplog):
    """
    Configure caplog to capture all log levels.
    
    This runs automatically for all tests.
    """
    caplog.set_level(logging.DEBUG)
    return caplog


# ============================================================
# TEST UTILITIES
# ============================================================

@pytest.fixture
def assert_sent_message():
    """
    Helper to assert SentMessage properties.
    
    Returns:
        Function that validates SentMessage
    """
    def _assert(result: SentMessage, check_ids: bool = True):
        logger.debug(f"✅ Asserting SentMessage: {result}")
        assert isinstance(result, SentMessage)
        if check_ids:
            assert result.zaap_id
            assert result.message_id
            assert result.id
            assert result.id == result.message_id
        logger.debug("✅ SentMessage validation passed")
    
    return _assert
