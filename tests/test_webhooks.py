"""
Unit tests for webhook message parsing.

Tests the parse_webhook_message function and all message type classes.
"""

import pytest
import logging
from datetime import datetime

from zapi_async.types import (
    parse_webhook_message,
    TextMessage,
    ImageMessage,
    VideoMessage,
    AudioMessage,
    DocumentMessage,
    StickerMessage,
    LocationMessage,
    ContactMessage,
    ReactionMessage,
    BaseWebhookMessage,
    is_text_message,
    is_image_message,
    is_media_message,
    is_group_message,
    is_from_me,
)

logger = logging.getLogger(__name__)


@pytest.mark.unit
@pytest.mark.webhook
class TestWebhookMessageParsing:
    """Test webhook message parsing."""
    
    def test_parse_text_message(self, mock_webhook_text_message, caplog):
        """Test parsing text message webhook."""
        logger.info("🧪 Testing parse_webhook_message (text)")
        
        message = parse_webhook_message(mock_webhook_text_message)
        
        assert isinstance(message, TextMessage)
        assert message.message == "Hello, this is a test message!"
        assert message.phone == "5511999999999"
        assert message.from_me is False
        assert message.is_group is False
        assert message.message_id == "MSG123ABC"
        
        logger.info(f"✅ Text message parsed: '{message.message}'")
    
    def test_parse_image_message(self, mock_webhook_image_message):
        """Test parsing image message webhook."""
        logger.info("🧪 Testing parse_webhook_message (image)")
        
        message = parse_webhook_message(mock_webhook_image_message)
        
        assert isinstance(message, ImageMessage)
        assert message.image_url == "https://example.com/image.jpg"
        assert message.caption == "Test image caption"
        assert message.width == 1920
        assert message.height == 1080
        assert message.view_once is False
        
        logger.info(f"✅ Image message parsed: {message.image_url}")
    
    def test_parse_reaction_message(self):
        """Test parsing reaction message."""
        logger.info("🧪 Testing parse_webhook_message (reaction)")
        
        payload = {
            "messageId": "REACT123",
            "phone": "5511999999999",
            "fromMe": False,
            "momment": 1632228955000,
            "status": "RECEIVED",
            "type": "ReceivedCallback",
            "instanceId": "INST123",
            "isGroup": False,
            "isNewsletter": False,
            "reaction": {
                "value": "❤️",
                "time": 1651878681150,
                "reactionBy": "5511999999999",
                "referencedMessage": {
                    "messageId": "REF_MSG_123",
                    "fromMe": True,
                    "phone": "5511999999999",
                    "participant": None
                }
            }
        }
        
        message = parse_webhook_message(payload)
        
        assert isinstance(message, ReactionMessage)
        assert message.emoji == "❤️"
        assert message.reaction_by == "5511999999999"
        assert message.referenced_message is not None
        assert message.referenced_message.message_id == "REF_MSG_123"
        
        logger.info(f"✅ Reaction parsed: {message.emoji}")
    
    def test_parse_unknown_message_fallback(self):
        """Test fallback to BaseWebhookMessage for unknown types."""
        logger.info("🧪 Testing parse_webhook_message (unknown type)")
        
        payload = {
            "messageId": "UNKNOWN123",
            "phone": "5511999999999",
            "fromMe": False,
            "momment": 1632228638000,
            "status": "RECEIVED",
            "type": "ReceivedCallback",
            "instanceId": "INST123",
            "isGroup": False,
            "isNewsletter": False,
            # No specific message type data
        }
        
        message = parse_webhook_message(payload)
        
        assert isinstance(message, BaseWebhookMessage)
        assert message.message_id == "UNKNOWN123"
        
        logger.info("✅ Unknown message fell back to BaseWebhookMessage")


@pytest.mark.unit
@pytest.mark.webhook
class TestMessageTypeHelpers:
    """Test message type helper functions."""
    
    def test_is_text_message(self, mock_webhook_text_message):
        """Test is_text_message helper."""
        logger.info("🧪 Testing is_text_message helper")
        
        message = parse_webhook_message(mock_webhook_text_message)
        
        assert is_text_message(message) is True
        assert is_image_message(message) is False
        assert is_media_message(message) is False
        
        logger.info("✅ is_text_message works correctly")
    
    def test_is_image_message(self, mock_webhook_image_message):
        """Test is_image_message helper."""
        logger.info("🧪 Testing is_image_message helper")
        
        message = parse_webhook_message(mock_webhook_image_message)
        
        assert is_image_message(message) is True
        assert is_text_message(message) is False
        assert is_media_message(message) is True  # Images are media
        
        logger.info("✅ is_image_message works correctly")
    
    def test_is_group_message(self):
        """Test is_group_message helper."""
        logger.info("🧪 Testing is_group_message helper")
        
        # Group message
        group_payload = {
            "messageId": "GRP123",
            "phone": "120363019502650977-group",
            "fromMe": False,
            "momment": 1632228638000,
            "status": "RECEIVED",
            "type": "ReceivedCallback",
            "instanceId": "INST123",
            "isGroup": True,
            "isNewsletter": False,
            "text": {"message": "Group message"}
        }
        
        message = parse_webhook_message(group_payload)
        
        assert is_group_message(message) is True
        assert message.is_group is True
        
        logger.info("✅ is_group_message works correctly")
    
    def test_is_from_me(self):
        """Test is_from_me helper."""
        logger.info("🧪 Testing is_from_me helper")
        
        # Message from me
        my_payload = {
            "messageId": "MY123",
            "phone": "5511999999999",
            "fromMe": True,
            "momment": 1632228638000,
            "status": "SENT",
            "type": "ReceivedCallback",
            "instanceId": "INST123",
            "isGroup": False,
            "isNewsletter": False,
            "text": {"message": "My message"}
        }
        
        message = parse_webhook_message(my_payload)
        
        assert is_from_me(message) is True
        assert message.from_me is True
        
        logger.info("✅ is_from_me works correctly")


@pytest.mark.unit
@pytest.mark.webhook
class TestMessageTypes:
    """Test individual message type classes."""
    
    def test_text_message_fields(self):
        """Test TextMessage specific fields."""
        logger.info("🧪 Testing TextMessage fields")
        
        payload = {
            "messageId": "TXT123",
            "phone": "5511999999999",
            "fromMe": False,
            "momment": 1632228638000,
            "status": "RECEIVED",
            "type": "ReceivedCallback",
            "instanceId": "INST123",
            "isGroup": False,
            "isNewsletter": False,
            "text": {
                "message": "Test message",
                "title": "Message Title",
                "description": "Message Description",
                "url": "https://example.com",
                "thumbnailUrl": "https://example.com/thumb.jpg"
            }
        }
        
        message = TextMessage.from_dict(payload)
        
        assert message.message == "Test message"
        assert message.title == "Message Title"
        assert message.description == "Message Description"
        assert message.url == "https://example.com"
        assert message.thumbnail_url == "https://example.com/thumb.jpg"
        
        logger.info("✅ TextMessage all fields parsed correctly")
    
    def test_image_message_fields(self):
        """Test ImageMessage specific fields."""
        logger.info("🧪 Testing ImageMessage fields")
        
        payload = {
            "messageId": "IMG123",
            "phone": "5511999999999",
            "fromMe": False,
            "momment": 1632228638000,
            "status": "RECEIVED",
            "type": "ReceivedCallback",
            "instanceId": "INST123",
            "isGroup": False,
            "isNewsletter": False,
            "image": {
                "imageUrl": "https://example.com/image.jpg",
                "thumbnailUrl": "https://example.com/thumb.jpg",
                "caption": "Image caption",
                "mimeType": "image/jpeg",
                "width": 1920,
                "height": 1080,
                "viewOnce": True
            }
        }
        
        message = ImageMessage.from_dict(payload)
        
        assert message.image_url == "https://example.com/image.jpg"
        assert message.mime_type == "image/jpeg"
        assert message.width == 1920
        assert message.height == 1080
        assert message.view_once is True
        
        logger.info("✅ ImageMessage all fields parsed correctly")
    
    def test_audio_message_ptt_flag(self):
        """Test AudioMessage PTT (voice) flag."""
        logger.info("🧪 Testing AudioMessage PTT flag")
        
        payload = {
            "messageId": "AUD123",
            "phone": "5511999999999",
            "fromMe": False,
            "momment": 1632228638000,
            "status": "RECEIVED",
            "type": "ReceivedCallback",
            "instanceId": "INST123",
            "isGroup": False,
            "isNewsletter": False,
            "audio": {
                "audioUrl": "https://example.com/audio.ogg",
                "mimeType": "audio/ogg",
                "seconds": 15,
                "ptt": True  # Voice message
            }
        }
        
        message = AudioMessage.from_dict(payload)
        
        assert message.ptt is True  # Is a voice message
        assert message.seconds == 15
        
        logger.info("✅ AudioMessage PTT flag works correctly")
    
    def test_location_message_coordinates(self):
        """Test LocationMessage coordinates."""
        logger.info("🧪 Testing LocationMessage coordinates")
        
        payload = {
            "messageId": "LOC123",
            "phone": "5511999999999",
            "fromMe": False,
            "momment": 1632228638000,
            "status": "RECEIVED",
            "type": "ReceivedCallback",
            "instanceId": "INST123",
            "isGroup": False,
            "isNewsletter": False,
            "location": {
                "latitude": -23.5505,
                "longitude": -46.6333,
                "name": "São Paulo",
                "address": "São Paulo, Brazil"
            }
        }
        
        message = LocationMessage.from_dict(payload)
        
        assert message.latitude == -23.5505
        assert message.longitude == -46.6333
        assert message.name == "São Paulo"
        
        logger.info(f"✅ Location: {message.name} ({message.latitude}, {message.longitude})")
    
    def test_message_timestamp_property(self,  mock_webhook_text_message):
        """Test timestamp property conversion."""
        logger.info("🧪 Testing message timestamp property")
        
        message = parse_webhook_message(mock_webhook_text_message)
        
        # Test timestamp conversion from milliseconds
        assert isinstance(message.timestamp, datetime)
        assert message.moment == 1632228638000
        
        logger.info(f"✅ Timestamp: {message.timestamp}")
    
    def test_raw_data_preservation(self, mock_webhook_text_message):
        """Test that raw webhook data is preserved."""
        logger.info("🧪 Testing raw data preservation")
        
        message = parse_webhook_message(mock_webhook_text_message)
        
        # Raw data should be stored
        assert message._raw is not None
        assert isinstance(message._raw, dict)
        assert message._raw["messageId"] == "MSG123ABC"
        
        logger.info("✅ Raw data preserved correctly")


@pytest.mark.unit
@pytest.mark.webhook
class TestEdgeCases:
    """Test edge cases in webhook parsing."""
    
    def test_missing_optional_fields(self):
        """Test parsing with missing optional fields."""
        logger.info("🧪 Testing parsing with missing optional fields")
        
        minimal_payload = {
            "messageId": "MIN123",
            "phone": "5511999999999",
            "fromMe": False,
            "momment": 1632228638000,
            "status": "RECEIVED",
            "type": "ReceivedCallback",
            "instanceId": "INST123",
            "isGroup": False,
            "isNewsletter": False,
            "text": {
                "message": "Minimal message"
                # No optional fields
            }
        }
        
        message = parse_webhook_message(minimal_payload)
        
        assert isinstance(message, TextMessage)
        assert message.message == "Minimal message"
        assert message.title is None
        assert message.description is None
        
        logger.info("✅ Missing optional fields handled correctly")
    
    def test_api_typo_handling(self):
        """
        Test handling of API typo ('descritpion' instead of 'description').
        
        Z-API has a typo in their API response.
        """
        logger.info("🧪 Testing API typo handling")
        
        payload = {
            "messageId": "TYPO123",
            "phone": "5511999999999",
            "fromMe": False,
            "momment": 1632228638000,
            "status": "RECEIVED",
            "type": "ReceivedCallback",
            "instanceId": "INST123",
            "isGroup": False,
            "isNewsletter": False,
            "text": {
                "message": "Test",
                "descritpion": "Typo in API"  # Note the typo
            }
        }
        
        message = parse_webhook_message(payload)
        
        # Should handle the typo
        assert message.description == "Typo in API"
        
        logger.info("✅ API typo handled correctly")
    
    def test_moment_vs_momment_typo(self):
        """Test handling of 'momment' typo in timestamp field."""
        logger.info("🧪 Testing moment/momment typo handling")
        
        # Test with correct spelling
        payload1 = {
            "messageId": "M1",
            "phone": "5511999999999",
            "fromMe": False,
            "moment": 1632228638000,  # Correct
            "status": "RECEIVED",
            "type": "ReceivedCallback",
            "instanceId": "INST123",
            "isGroup": False,
            "isNewsletter": False,
            "text": {"message": "Test"}
        }
        
        message1 = parse_webhook_message(payload1)
        assert message1.moment > 0
        
        # Test with typo (actual Z-API response)
        payload2 = {
            "messageId": "M2",
            "phone": "5511999999999",
            "fromMe": False,
            "momment": 1632228638000,  # Typo (actual API)
            "status": "RECEIVED",
            "type": "ReceivedCallback",
            "instanceId": "INST123",
            "isGroup": False,
            "isNewsletter": False,
            "text": {"message": "Test"}
        }
        
        message2 = parse_webhook_message(payload2)
        assert message2.moment > 0
        
        logger.info("✅ Both spellings handled correctly")
