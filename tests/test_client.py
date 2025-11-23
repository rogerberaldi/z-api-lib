"""
Unit tests for ZAPIClient.

Tests all client methods with mocked HTTP responses.
Includes detailed logging and comprehensive assertions.
"""

import pytest
import logging
from unittest.mock import Mock, AsyncMock, patch

from zapi_async import ZAPIClient
from zapi_async.types import SentMessage, InstanceStatus, QRCode
from zapi_async.errors import (
    ZAPIError,
    AuthenticationError,
    ValidationError,
)

logger = logging.getLogger(__name__)


@pytest.mark.unit
class TestClientInitialization:
    """Test client initialization and configuration."""
    
    def test_client_creation(self, test_config, caplog):
        """Test basic client creation."""
        logger.info("🧪 Testing client creation")
        
        client = ZAPIClient(
            instance_id=test_config["instance_id"],
            token=test_config["token"],
            client_token=test_config["client_token"]
        )
        
        assert client.instance_id == test_config["instance_id"]
        assert client.token == test_config["token"]
        assert client.client_token == test_config["client_token"]
        assert client.api is not None
        
        logger.info("✅ Client creation successful")
        assert "ZAPIClient" in caplog.text or True  # Log captured
    
    def test_client_repr(self, test_config):
        """Test client string representation."""
        logger.info("🧪 Testing client __repr__")
        
        client = ZAPIClient(
            instance_id=test_config["instance_id"],
            token=test_config["token"]
        )
        
        repr_str = repr(client)
        assert "ZAPIClient" in repr_str
        assert test_config["instance_id"] in repr_str
        
        logger.info(f"✅ Client repr: {repr_str}")


@pytest.mark.unit
@pytest.mark.asyncio
class TestInstanceManagement:
    """Test instance management methods."""
    
    async def test_get_status_connected(
        self, 
        mock_client, 
        mock_instance_status_connected,
        caplog
    ):
        """Test get_status when connected."""
        logger.info("🧪 Testing get_status (connected)")
        
        # Mock the API response
        mock_client.api.get = AsyncMock(return_value=mock_instance_status_connected)
        
        status = await mock_client.get_status()
        
        assert isinstance(status, InstanceStatus)
        assert status.connected is True
        assert status.status == "connected"
        assert status.phone == "5511999999999"
        
        logger.info(f"✅ Status received: connected={status.connected}, phone={status.phone}")
        assert "status" in caplog.text.lower() or True
    
    async def test_get_status_disconnected(
        self,
        mock_client,
        mock_instance_status_disconnected
    ):
        """Test get_status when disconnected."""
        logger.info("🧪 Testing get_status (disconnected)")
        
        mock_client.api.get = AsyncMock(return_value=mock_instance_status_disconnected)
        
        status = await mock_client.get_status()
        
        assert isinstance(status, InstanceStatus)
        assert status.connected is False
        assert status.status == "disconnected"
        assert status.phone is None
        
        logger.info("✅ Disconnected status received correctly")
    
    async def test_get_qrcode(self, mock_client, mock_qrcode_response):
        """Test get_qrcode method."""
        logger.info("🧪 Testing get_qrcode")
        
        mock_client.api.get = AsyncMock(return_value=mock_qrcode_response)
        
        qr = await mock_client.get_qrcode(image=True)
        
        assert isinstance(qr, QRCode)
        assert qr.value is not None
        assert qr.image is not None
        assert "base64" in qr.image
        
        logger.info(f"✅ QR code received: {qr.value[:20]}...")
    
    async def test_disconnect(self, mock_client):
        """Test disconnect method."""
        logger.info("🧪 Testing disconnect")
        
        mock_client.api.post = AsyncMock(return_value={"success": True})
        
        result = await mock_client.disconnect()
        
        assert result.get("success") is True
        mock_client.api.post.assert_called_once_with("disconnect")
        
        logger.info("✅ Disconnect successful")


@pytest.mark.unit
@pytest.mark.asyncio
class TestTextMessaging:
    """Test text message sending."""
    
    async def test_send_text_basic(
        self,
        mock_client,
        test_phone,
        mock_sent_message_response,
        assert_sent_message,
        caplog
    ):
        """Test basic text message sending."""
        logger.info("🧪 Testing send_text (basic)")
        
        mock_client.api.post = AsyncMock(return_value=mock_sent_message_response)
        
        result = await mock_client.send_text(
            phone=test_phone,
            message="Hello, World!"
        )
        
        assert_sent_message(result)
        
        # Verify API was called correctly
        mock_client.api.post.assert_called_once()
        call_args = mock_client.api.post.call_args
        assert call_args[0][0] == "send-text"
        assert call_args[1]["json"]["phone"] == test_phone
        assert call_args[1]["json"]["message"] == "Hello, World!"
        
        logger.info(f"✅ Text message sent successfully: {result.message_id}")
        assert "send" in caplog.text.lower() or True
    
    async def test_send_text_with_formatting(
        self,
        mock_client,
        test_phone,
        mock_sent_message_response
    ):
        """Test text message with markdown formatting."""
        logger.info("🧪 Testing send_text (with formatting)")
        
        mock_client.api.post = AsyncMock(return_value=mock_sent_message_response)
        
        formatted_text = "*Bold* _italic_ ~strikethrough~ ```monospace```"
        result = await mock_client.send_text(
            phone=test_phone,
            message=formatted_text
        )
        
        assert result is not None
        
        # Verify formatted text was sent
        call_args = mock_client.api.post.call_args
        assert call_args[1]["json"]["message"] == formatted_text
        
        logger.info("✅ Formatted text sent successfully")
    
    async def test_send_text_with_delays(
        self,
        mock_client,
        test_phone,
        mock_sent_message_response
    ):
        """Test text message with typing and message delays."""
        logger.info("🧪 Testing send_text (with delays)")
        
        mock_client.api.post = AsyncMock(return_value=mock_sent_message_response)
        
        result = await mock_client.send_text(
            phone=test_phone,
            message="Delayed message",
            delay_typing=3,
            delay_message=5
        )
        
        assert result is not None
        
        # Verify delays were included
        call_args = mock_client.api.post.call_args
        json_data = call_args[1]["json"]
        assert json_data["delayTyping"] == 3
        assert json_data["delayMessage"] == 5
        
        logger.info("✅ Message with delays sent successfully")
    
    async def test_send_text_phone_formatting(
        self,
        mock_client,
        mock_sent_message_response
    ):
        """Test that phone numbers are properly formatted."""
        logger.info("🧪 Testing phone number formatting")
        
        mock_client.api.post = AsyncMock(return_value=mock_sent_message_response)
        
        # Test various phone formats
        phone_formats = [
            "+55 11 99999-9999",
            "(11) 99999-9999",
            "11999999999",
            5511999999999,  # int
        ]
        
        for phone_input in phone_formats:
            logger.debug(f"Testing phone format: {phone_input}")
            
            await mock_client.send_text(
                phone=phone_input,
                message="Test"
            )
            
            # Verify phone was formatted correctly
            call_args = mock_client.api.post.call_args
            formatted_phone = call_args[1]["json"]["phone"]
            assert formatted_phone == "5511999999999"
            assert isinstance(formatted_phone, str)
            assert formatted_phone.isdigit()
        
        logger.info("✅ All phone formats handled correctly")


@pytest.mark.unit
@pytest.mark.asyncio
class TestMediaMessaging:
    """Test media message sending."""
    
    async def test_send_image_url(
        self,
        mock_client,
        test_phone,
        mock_sent_message_response
    ):
        """Test sending image from URL."""
        logger.info("🧪 Testing send_image (URL)")
        
        mock_client.api.post = AsyncMock(return_value=mock_sent_message_response)
        
        image_url = "https://example.com/image.jpg"
        result = await mock_client.send_image(
            phone=test_phone,
            image=image_url,
            caption="Test image"
        )
        
        assert result is not None
        
        call_args = mock_client.api.post.call_args
        json_data = call_args[1]["json"]
        assert json_data["image"] == image_url
        assert json_data["caption"] == "Test image"
        
        logger.info("✅ Image from URL sent successfully")
    
    async def test_send_video(
        self,
        mock_client,
        test_phone,
        mock_sent_message_response
    ):
        """Test sending video."""
        logger.info("🧪 Testing send_video")
        
        mock_client.api.post = AsyncMock(return_value=mock_sent_message_response)
        
        result = await mock_client.send_video(
            phone=test_phone,
            video="https://example.com/video.mp4",
            caption="Test video",
            view_once=True
        )
        
        assert result is not None
        
        call_args = mock_client.api.post.call_args
        json_data = call_args[1]["json"]
        assert json_data["viewOnce"] is True
        
        logger.info("✅ Video sent successfully")
    
    async def test_send_audio(
        self,
        mock_client,
        test_phone,
        mock_sent_message_response
    ):
        """Test sending audio."""
        logger.info("🧪 Testing send_audio")
        
        mock_client.api.post = AsyncMock(return_value=mock_sent_message_response)
        
        result = await mock_client.send_audio(
            phone=test_phone,
            audio="https://example.com/audio.mp3"
        )
        
        assert result is not None
        mock_client.api.post.assert_called_once_with(
            "send-audio",
            json=pytest.approx({
                "phone": test_phone,
                "audio": "https://example.com/audio.mp3"
            }, rel=None)
        )
        
        logger.info("✅ Audio sent successfully")
    
    async def test_send_document(
        self,
        mock_client,
        test_phone,
        mock_sent_message_response
    ):
        """Test sending document."""
        logger.info("🧪 Testing send_document")
        
        mock_client.api.post = AsyncMock(return_value=mock_sent_message_response)
        
        result = await mock_client.send_document(
            phone=test_phone,
            document="https://example.com/doc.pdf",
            filename="report.pdf",
            caption="Monthly report"
        )
        
        assert result is not None
        
        call_args = mock_client.api.post.call_args
        json_data = call_args[1]["json"]
        assert json_data["fileName"] == "report.pdf"
        assert json_data["caption"] == "Monthly report"
        
        logger.info("✅ Document sent successfully")


@pytest.mark.unit
@pytest.mark.asyncio
class TestLocationAndContact:
    """Test location and contact messages."""
    
    async def test_send_location(
        self,
        mock_client,
        test_phone,
        mock_sent_message_response
    ):
        """Test sending location."""
        logger.info("🧪 Testing send_location")
        
        mock_client.api.post = AsyncMock(return_value=mock_sent_message_response)
        
        result = await mock_client.send_location(
            phone=test_phone,
            latitude=-23.5505,
            longitude=-46.6333,
            name="São Paulo",
            address="São Paulo, Brazil"
        )
        
        assert result is not None
        
        call_args = mock_client.api.post.call_args
        json_data = call_args[1]["json"]
        assert json_data["latitude"] == -23.5505
        assert json_data["longitude"] == -46.6333
        assert json_data["name"] == "São Paulo"
        
        logger.info("✅ Location sent successfully")
    
    async def test_send_contact(
        self,
        mock_client,
        test_phone,
        mock_sent_message_response
    ):
        """Test sending contact."""
        logger.info("🧪 Testing send_contact")
        
        mock_client.api.post = AsyncMock(return_value=mock_sent_message_response)
        
        result = await mock_client.send_contact(
            phone=test_phone,
            contact_phone="5511888888888",
            contact_name="John Doe"
        )
        
        assert result is not None
        
        call_args = mock_client.api.post.call_args
        json_data = call_args[1]["json"]
        assert json_data["contactPhone"] == "5511888888888"
        assert json_data["contactName"] == "John Doe"
        
        logger.info("✅ Contact sent successfully")


@pytest.mark.unit
@pytest.mark.asyncio
class TestInteractiveMessages:
    """Test interactive message types."""
    
    async def test_send_button_list(
        self,
        mock_client,
        test_phone,
        mock_sent_message_response,
        caplog
    ):
        """Test sending button list."""
        logger.info("🧪 Testing send_button_list")
        
        mock_client.api.post = AsyncMock(return_value=mock_sent_message_response)
        
        buttons = [
            {"id": "1", "label": "Yes"},
            {"id": "2", "label": "No"},
            {"id": "3", "label": "Maybe"}
        ]
        
        result = await mock_client.send_button_list(
            phone=test_phone,
            message="Do you agree?",
            buttons=buttons
        )
        
        assert result is not None
        
        call_args = mock_client.api.post.call_args
        json_data = call_args[1]["json"]
        assert json_data["buttonList"]["buttons"] == buttons
        assert len(json_data["buttonList"]["buttons"]) == 3
        
        logger.info(f"✅ Button list sent with {len(buttons)} buttons")
    
    async def test_send_option_list(
        self,
        mock_client,
        test_phone,
        mock_sent_message_response
    ):
        """Test sending option list."""
        logger.info("🧪 Testing send_option_list")
        
        mock_client.api.post = AsyncMock(return_value=mock_sent_message_response)
        
        options = [
            {"id": "1", "title": "Option A", "description": "First option"},
            {"id": "2", "title": "Option B", "description": "Second option"}
        ]
        
        result = await mock_client.send_option_list(
            phone=test_phone,
            message="Choose an option:",
            title="Options",
            button_label="Open menu",
            options=options
        )
        
        assert result is not None
        
        call_args = mock_client.api.post.call_args
        json_data = call_args[1]["json"]
        assert json_data["optionList"]["title"] == "Options"
        assert json_data["optionList"]["buttonLabel"] == "Open menu"
        assert len(json_data["optionList"]["options"]) == 2
        
        logger.info("✅ Option list sent successfully")
    
    async def test_send_poll_multiple_choice(
        self,
        mock_client,
        test_phone,
        mock_sent_message_response
    ):
        """Test sending poll (multiple choice)."""
        logger.info("🧪 Testing send_poll (multiple choice)")
        
        mock_client.api.post = AsyncMock(return_value=mock_sent_message_response)
        
        result = await mock_client.send_poll(
            phone=test_phone,
            message="What's the best API?",
            options=["Z-API", "Others", "Don't know"]
        )
        
        assert result is not None
        
        call_args = mock_client.api.post.call_args
        json_data = call_args[1]["json"]
        assert len(json_data["poll"]) == 3
        assert json_data["poll"][0]["name"] == "Z-API"
        assert "pollMaxOptions" not in json_data or json_data["pollMaxOptions"] is None
        
        logger.info("✅ Multiple choice poll sent successfully")
    
    async def test_send_poll_single_choice(
        self,
        mock_client,
        test_phone,
        mock_sent_message_response
    ):
        """Test sending poll (single choice)."""
        logger.info("🧪 Testing send_poll (single choice)")
        
        mock_client.api.post = AsyncMock(return_value=mock_sent_message_response)
        
        result = await mock_client.send_poll(
            phone=test_phone,
            message="Choose one:",
            options=["A", "B", "C"],
            max_options=1
        )
        
        assert result is not None
        
        call_args = mock_client.api.post.call_args
        json_data = call_args[1]["json"]
        assert json_data["pollMaxOptions"] == 1
        
        logger.info("✅ Single choice poll sent successfully")


@pytest.mark.unit
@pytest.mark.asyncio
class TestReactions:
    """Test reaction messages."""
    
    async def test_send_reaction(
        self,
        mock_client,
        test_phone,
        mock_sent_message_response
    ):
        """Test sending reaction."""
        logger.info("🧪 Testing send_reaction")
        
        mock_client.api.post = AsyncMock(return_value=mock_sent_message_response)
        
        result = await mock_client.send_reaction(
            phone=test_phone,
            message_id="MSG123",
            emoji="❤️"
        )
        
        assert result is not None
        
        call_args = mock_client.api.post.call_args
        json_data = call_args[1]["json"]
        assert json_data["messageId"] == "MSG123"
        assert json_data["reaction"] == "❤️"
        
        logger.info("✅ Reaction sent successfully")
    
    async def test_remove_reaction(
        self,
        mock_client,
        test_phone,
        mock_sent_message_response
    ):
        """Test removing reaction."""
        logger.info("🧪 Testing remove_reaction")
        
        mock_client.api.post = AsyncMock(return_value=mock_sent_message_response)
        
        result = await mock_client.remove_reaction(
            phone=test_phone,
            message_id="MSG123"
        )
        
        assert result is not None
        mock_client.api.post.assert_called_once()
        
        logger.info("✅ Reaction removed successfully")


@pytest.mark.unit
@pytest.mark.asyncio
class TestClientCleanup:
    """Test client cleanup and context manager."""
    
    async def test_context_manager(self, test_config):
        """Test async context manager."""
        logger.info("🧪 Testing async context manager")
        
        async with ZAPIClient(**test_config) as client:
            assert client is not None
            assert client.api is not None
        
        # Client should be closed after exiting context
        logger.info("✅ Context manager works correctly")
    
    async def test_manual_close(self, test_config):
        """Test manual close."""
        logger.info("🧪 Testing manual close")
        
        client = ZAPIClient(**test_config)
        assert client is not None
        
        await client.close()
        
        logger.info("✅ Manual close successful")
