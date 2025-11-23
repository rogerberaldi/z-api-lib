"""
Integration tests for Z-API.

WARNING: These tests make REAL API calls to Z-API.
Only run with valid credentials and a test instance.

Set environment variables:
    - ZAPI_INSTANCE_ID
    - ZAPI_TOKEN
    - ZAPI_CLIENT_TOKEN
    - ZAPI_TEST_PHONE (optional, phone to send test messages)

Run with: pytest tests/test_integration.py -v -s --integration
"""

import pytest
import os
import logging
import asyncio

from zapi_async import ZAPIClient
from zapi_async.errors import AuthenticationError, InstanceError

logger = logging.getLogger(__name__)


# Skip all integration tests by default
pytestmark = pytest.mark.integration


def check_credentials():
    """Check if integration test credentials are available."""
    required = ["ZAPI_INSTANCE_ID", "ZAPI_TOKEN"]
    missing = [var for var in required if not os.getenv(var)]
    
    if missing:
        pytest.skip(f"Missing credentials: {', '.join(missing)}")


@pytest.fixture
def integration_config():
    """Get integration test configuration from environment."""
    check_credentials()
    
    return {
        "instance_id": os.getenv("ZAPI_INSTANCE_ID"),
        "token": os.getenv("ZAPI_TOKEN"),
        "client_token": os.getenv("ZAPI_CLIENT_TOKEN"),
        "test_phone": os.getenv("ZAPI_TEST_PHONE", "5511999999999"),
    }


@pytest.mark.asyncio
@pytest.mark.slow
class TestRealAPIConnection:
    """Test real API connection and authentication."""
    
    async def test_get_status_real(self, integration_config, caplog):
        """Test getting real instance status."""
        logger.info("🔌 Testing REAL API connection")
        logger.warning("⚠️  This will make a real API call!")
        
        async with ZAPIClient(
            instance_id=integration_config["instance_id"],
            token=integration_config["token"],
            client_token=integration_config["client_token"]
        ) as client:
            
            status = await client.get_status()
            
            logger.info(f"📊 Instance Status:")
            logger.info(f"  Connected: {status.connected}")
            logger.info(f"  Status: {status.status}")
            logger.info(f"  Phone: {status.phone}")
            
            assert status is not None
            assert hasattr(status, "connected")
            
            if status.connected:
                logger.info("✅ Instance is connected")
                if status.phone:
                    logger.info(f"📱 Connected phone: {status.phone}")
                else:
                    logger.warning("⚠️  Connected but phone number not returned in status")
            else:
                logger.warning("⚠️  Instance is not connected - some tests may fail")
        
        logger.info("✅ Real API connection test complete")


@pytest.mark.asyncio
@pytest.mark.slow
class TestRealMessaging:
    """
    Test real message sending.
    
    WARNING: These tests will send actual messages!
    Only run if you have a test phone number configured.
    """
    
    async def test_send_text_real(self, integration_config):
        """Test sending real text message."""
        if not integration_config["test_phone"]:
            pytest.skip("No test phone configured")
        
        logger.info("📤 Testing REAL text message send")
        logger.warning(f"⚠️  Will send message to: {integration_config['test_phone']}")
        
        async with ZAPIClient(
            instance_id=integration_config["instance_id"],
            token=integration_config["token"],
            client_token=integration_config["client_token"]
        ) as client:
            
            # Check connection first
            status = await client.get_status()
            if not status.connected:
                pytest.skip("Instance not connected")
            
            result = await client.send_text(
                phone=integration_config["test_phone"],
                message="🧪 Test message from zapi_async integration tests"
            )
            
            logger.info(f"✅ Message sent!")
            logger.info(f"  ZaapID: {result.zaap_id}")
            logger.info(f"  MessageID: {result.message_id}")
            
            assert result.message_id is not None
            assert result.zaap_id is not None
    
    async def test_send_location_real(self, integration_config):
        """Test sending real location."""
        if not integration_config["test_phone"]:
            pytest.skip("No test phone configured")
        
        logger.info("📍 Testing REAL location send")
        
        async with ZAPIClient(
            instance_id=integration_config["instance_id"],
            token=integration_config["token"],
            client_token=integration_config["client_token"]
        ) as client:
            
            status = await client.get_status()
            if not status.connected:
                pytest.skip("Instance not connected")
            
            result = await client.send_location(
                phone=integration_config["test_phone"],
                latitude=-23.5505,
                longitude=-46.6333,
                name="São Paulo",
                address="São Paulo, Brazil"
            )
            
            logger.info(f"✅ Location sent: {result.message_id}")
            
            assert result.message_id is not None


@pytest.mark.asyncio
@pytest.mark.slow
class TestRealInteractiveMessages:
    """Test real interactive messages."""
    
    async def test_send_button_list_real(self, integration_config):
        """Test sending real button list."""
        if not integration_config["test_phone"]:
            pytest.skip("No test phone configured")
        
        logger.info("🔘 Testing REAL button list send")
        
        async with ZAPIClient(
            instance_id=integration_config["instance_id"],
            token=integration_config["token"],
            client_token=integration_config["client_token"]
        ) as client:
            
            status = await client.get_status()
            if not status.connected:
                pytest.skip("Instance not connected")
            
            buttons = [
                {"id": "1", "label": "✅ Sim"},
                {"id": "2", "label": "❌ Não"},
            ]
            
            result = await client.send_button_list(
                phone=integration_config["test_phone"],
                message="🧪 Teste de botões - zapi_async",
                buttons=buttons
            )
            
            logger.info(f"✅ Button list sent: {result.message_id}")
            
            assert result.message_id is not None
    
    async def test_send_poll_real(self, integration_config):
        """Test sending real poll."""
        if not integration_config["test_phone"]:
            pytest.skip("No test phone configured")
        
        logger.info("📊 Testing REAL poll send")
        
        async with ZAPIClient(
            instance_id=integration_config["instance_id"],
            token=integration_config["token"],
            client_token=integration_config["client_token"]
        ) as client:
            
            status = await client.get_status()
            if not status.connected:
                pytest.skip("Instance not connected")
            
            result = await client.send_poll(
                phone=integration_config["test_phone"],
                message="🧪 Qual a melhor API para WhatsApp?",
                options=["Z-API", "Outras"],
                max_options=1
            )
            
            logger.info(f"✅ Poll sent: {result.message_id}")
            
            assert result.message_id is not None


@pytest.mark.asyncio
class TestErrorHandling:
    """Test error handling with real API."""
    
    async def test_invalid_credentials(self):
        """Test error with invalid credentials."""
        logger.info("🔐 Testing invalid credentials")
        
        async with ZAPIClient(
            instance_id="INVALID",
            token="INVALID",
            client_token="INVALID"
        ) as client:
            
            # Should raise AuthenticationError or similar
            with pytest.raises((AuthenticationError, InstanceError, Exception)):
                await client.get_status()
        
        logger.info("✅ Invalid credentials handled correctly")


@pytest.mark.asyncio
@pytest.mark.slow
class TestStressTest:
    """Stress test with multiple concurrent requests."""
    
    async def test_concurrent_status_checks(self, integration_config):
        """Test multiple concurrent status checks."""
        logger.info("⚡ Testing concurrent API calls")
        
        async with ZAPIClient(
            instance_id=integration_config["instance_id"],
            token=integration_config["token"],
            client_token=integration_config["client_token"]
        ) as client:
            
            # Make 5 concurrent status checks
            tasks = [client.get_status() for _ in range(5)]
            results = await asyncio.gather(*tasks)
            
            assert len(results) == 5
            for status in results:
                assert status is not None
            
            logger.info(f"✅ {len(results)} concurrent requests successful")


# ============================================================
# HELPER FOR MANUAL TESTING
# ============================================================

if __name__ == "__main__":
    """
    Run integration tests manually.
    
    Usage:
        export ZAPI_INSTANCE_ID="your_instance"
        export ZAPI_TOKEN="your_token"
        export ZAPI_CLIENT_TOKEN="your_client_token"
        export ZAPI_TEST_PHONE="your_test_phone"
        
        python tests/test_integration.py
    """
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Check credentials
    if not all([os.getenv("ZAPI_INSTANCE_ID"), os.getenv("ZAPI_TOKEN")]):
        print("❌ Missing credentials!")
        print("Set ZAPI_INSTANCE_ID and ZAPI_TOKEN environment variables")
        sys.exit(1)
    
    print("=" * 60)
    print("🧪 Running Integration Tests Manually")
    print("=" * 60)
    
    # Run pytest programmatically
    pytest.main([
        __file__,
        "-v",
        "-s",
        "--log-cli-level=INFO",
        "-m", "integration"
    ])
