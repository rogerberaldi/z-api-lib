"""
Unit tests for helper functions.

Tests all utility functions in _helpers.py.
"""

import pytest
import logging
from pathlib import Path

from zapi_async._helpers import (
    format_phone,
    is_url,
    is_base64,
    is_group_id,
    encode_base64,
    get_mime_type,
    format_text_markdown,
    build_request_body,
)
from zapi_async.errors import ValidationError

logger = logging.getLogger(__name__)


@pytest.mark.unit
class TestPhoneFormatting:
    """Test phone number formatting."""
    
    def test_format_phone_with_symbols(self, caplog):
        """Test formatting phone with symbols."""
        logger.info("🧪 Testing format_phone with symbols")
        
        # Various formats with symbols
        test_cases = [
            ("+55 11 99999-9999", "5511999999999"),
            ("(11) 99999-9999", "11999999999"),
            ("+55-11-99999-9999", "5511999999999"),
            ("55 (11) 99999-9999", "5511999999999"),
        ]
        
        for input_phone, expected in test_cases:
            logger.debug(f"Testing: {input_phone} → {expected}")
            result = format_phone(input_phone)
            # The implementation only strips non-digits, it doesn't add country code
            # So we just check if it matches the digits
            assert result == expected
            assert result.isdigit()
        
        logger.info("✅ All phone formats with symbols handled")
    
    def test_format_phone_integer(self):
        """Test formatting integer phone number."""
        logger.info("🧪 Testing format_phone with integer")
        
        result = format_phone(5511999999999)
        
        assert result == "5511999999999"
        assert isinstance(result, str)
        
        logger.info("✅ Integer phone formatted correctly")
    
    def test_format_phone_already_clean(self):
        """Test formatting already clean phone."""
        logger.info("🧪 Testing format_phone with clean input")
        
        clean_phone = "5511999999999"
        result = format_phone(clean_phone)
        
        assert result == clean_phone
        
        logger.info("✅ Clean phone passed through")
    
    def test_format_phone_with_country_code(self):
        """Test various country codes."""
        logger.info("🧪 Testing format_phone with country codes")
        
        test_cases = [
            ("+1 555 123 4567", "15551234567"),  # US
            ("+44 20 1234 5678", "442012345678"),  # UK
            ("+55 11 9 9999-9999", "5511999999999"),  # Brazil
        ]
        
        for input_phone, expected in test_cases:
            result = format_phone(input_phone)
            assert result == expected
        
        logger.info("✅ Country codes handled correctly")


@pytest.mark.unit
class TestURLValidation:
    """Test URL validation."""
    
    def test_is_url_valid_http(self):
        """Test valid HTTP URLs."""
        logger.info("🧪 Testing is_url with valid HTTP")
        
        urls = [
            "http://example.com",
            "https://example.com/path",
            "https://example.com/path?query=value",
        ]
        
        for url in urls:
            assert is_url(url) is True
            logger.debug(f"✓ {url} is valid")
        
        logger.info("✅ HTTP URLs validated correctly")
    
    def test_is_url_invalid(self):
        """Test invalid URLs."""
        logger.info("🧪 Testing is_url with invalid URLs")
        
        invalid = [
            "not a url",
            "/local/path",
            "file.txt",
            "",
        ]
        
        for invalid_url in invalid:
            assert is_url(invalid_url) is False
            logger.debug(f"✗ {invalid_url} is invalid")
        
        logger.info("✅ Invalid URLs rejected correctly")


@pytest.mark.unit
class TestBase64Detection:
    """Test base64 string detection."""
    
    def test_is_base64_valid(self):
        """Test valid base64 strings."""
        logger.info("🧪 Testing is_base64 with valid strings")
        
        valid_base64 = [
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
            "data:image/jpeg;base64,/9j/4AAQSkZJRg==",
        ]
        
        for b64 in valid_base64:
            assert is_base64(b64) is True
        
        logger.info("✅ Base64 strings detected correctly")
    
    def test_is_base64_invalid(self):
        """Test non-base64 strings."""
        logger.info("🧪 Testing is_base64 with invalid strings")
        
        invalid = [
            "https://example.com/image.jpg",
            "not base64",
            "/path/to/file.jpg",
        ]
        
        for invalid_str in invalid:
            assert is_base64(invalid_str) is False
        
        logger.info("✅ Non-base64 strings rejected correctly")


@pytest.mark.unit
class TestGroupIDDetection:
    """Test group ID detection."""
    
    def test_is_group_id_new_format(self):
        """Test new group ID format."""
        logger.info("🧪 Testing is_group_id (new format)")
        
        group_ids = [
            "120363019502650977-group",
            "123456789012345678-group",
        ]
        
        for group_id in group_ids:
            assert is_group_id(group_id) is True
            logger.debug(f"✓ {group_id} is group")
        
        logger.info("✅ New format group IDs detected")
    
    def test_is_group_id_old_format(self):
        """Test old group ID format."""
        logger.info("🧪 Testing is_group_id (old format)")
        
        group_ids = [
            "5511999999999-1234567890",
            "5521888888888-9876543210",
        ]
        
        for group_id in group_ids:
            assert is_group_id(group_id) is True
        
        logger.info("✅ Old format group IDs detected")
    
    def test_is_group_id_personal_chat(self):
        """Test personal chat numbers."""
        logger.info("🧪 Testing is_group_id with personal chats")
        
        personal = [
            "5511999999999",
            "1234567890",
        ]
        
        for phone in personal:
            assert is_group_id(phone) is False
            logger.debug(f"✗ {phone} is not group")
        
        logger.info("✅ Personal chats rejected correctly")


@pytest.mark.unit
class TestMIMETypeDetection:
    """Test MIME type detection."""
    
    def test_get_mime_type_common_extensions(self):
        """Test common file extensions."""
        logger.info("🧪 Testing get_mime_type with common extensions")
        
        test_cases = [
            ("image.jpg", "image/jpeg"),
            ("image.jpeg", "image/jpeg"),
            ("image.png", "image/png"),
            ("video.mp4", "video/mp4"),
            ("audio.mp3", "audio/mpeg"),
            ("document.pdf", "application/pdf"),
        ]
        
        for filename, expected_mime in test_cases:
            result = get_mime_type(filename)
            assert result == expected_mime
            logger.debug(f"{filename} → {result}")
        
        logger.info("✅ Common MIME types detected correctly")
    
    def test_get_mime_type_unknown(self):
        """Test unknown file extension."""
        logger.info("🧪 Testing get_mime_type with unknown extension")
        
        # Using a truly random extension that shouldn't exist
        result = get_mime_type("file.trulyunknownextension")
        
        assert result == "application/octet-stream"
        
        logger.info("✅ Unknown extension defaults correctly")


@pytest.mark.unit
class TestWhatsAppTextFormatting:
    """Test WhatsApp text formatting helpers."""
    
    def test_format_whatsapp_text_bold(self):
        """Test bold formatting."""
        logger.info("🧪 Testing format_whatsapp_text (bold)")
        
        result = format_text_markdown("test", bold=True)
        
        assert result == "*test*"
        
        logger.info("✅ Bold formatting works")
    
    def test_format_whatsapp_text_italic(self):
        """Test italic formatting."""
        logger.info("🧪 Testing format_whatsapp_text (italic)")
        
        result = format_text_markdown("test", italic=True)
        
        assert result == "_test_"
        
        logger.info("✅ Italic formatting works")
    
    def test_format_whatsapp_text_strikethrough(self):
        """Test strikethrough formatting."""
        logger.info("🧪 Testing format_whatsapp_text (strikethrough)")
        
        result = format_text_markdown("test", strikethrough=True)
        
        assert result == "~test~"
        
        logger.info("✅ Strikethrough formatting works")
    
    def test_format_whatsapp_text_monospace(self):
        """Test monospace formatting."""
        logger.info("🧪 Testing format_whatsapp_text (monospace)")
        
        result = format_text_markdown("test", monospace=True)
        
        assert result == "```test```"
        
        logger.info("✅ Monospace formatting works")
    
    def test_format_whatsapp_text_combinations(self):
        """Test combination of formatting."""
        logger.info("🧪 Testing format_whatsapp_text (combinations)")
        
        # Bold + Italic
        result = format_text_markdown("test", bold=True, italic=True)
        assert "*" in result and "_" in result
        
        logger.info("✅ Format combinations work")


@pytest.mark.unit
class TestRequestBodyBuilder:
    """Test build_request_body helper."""
    
    def test_build_request_body_basic(self):
        """Test basic request body building."""
        logger.info("🧪 Testing build_request_body (basic)")
        
        body = build_request_body(
            phone="5511999999999",
            message="Test message"
        )
        
        assert body["phone"] == "5511999999999"
        assert body["message"] == "Test message"
        
        logger.info("✅ Basic request body built")
    
    def test_build_request_body_removes_none(self):
        """Test that None values are removed."""
        logger.info("🧪 Testing build_request_body (None removal)")
        
        body = build_request_body(
            phone="5511999999999",
            message="Test",
            caption=None,  # Should be removed
            delay_message=5,
            view_once=None  # Should be removed
        )
        
        assert "phone" in body
        assert "message" in body
        assert "caption" not in body
        assert "delay_message" in body
        assert "view_once" not in body
        
        logger.info("✅ None values removed correctly")
    

    
    def test_build_request_body_empty(self):
        """Test building empty body."""
        logger.info("🧪 Testing build_request_body (empty)")
        
        body = build_request_body()
        
        assert isinstance(body, dict)
        assert len(body) == 0
        
        logger.info("✅ Empty body handled")


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases in helpers."""
    
    def test_format_phone_empty_string(self):
        """Test formatting empty phone."""
        logger.info("🧪 Testing format_phone with empty string")
        
        with pytest.raises(ValidationError):
            format_phone("")
        
        logger.info("✅ Empty phone handled")
    
    def test_format_phone_whitespace_only(self):
        """Test formatting whitespace-only phone."""
        logger.info("🧪 Testing format_phone with whitespace")
        
        with pytest.raises(ValidationError):
            format_phone("   ")
        
        logger.info("✅ Whitespace phone handled")
    
    def test_get_mime_type_no_extension(self):
        """Test MIME type for file without extension."""
        logger.info("🧪 Testing get_mime_type without extension")
        
        result = get_mime_type("filename")
        
        assert result == "application/octet-stream"
        
        logger.info("✅ No extension handled")
