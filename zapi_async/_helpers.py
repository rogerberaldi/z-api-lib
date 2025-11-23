"""Internal helper functions for zapi_async."""

from __future__ import annotations
import re
import base64
import mimetypes
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .errors import ValidationError


def format_phone(phone: str | int) -> str:
    """
    Format phone number for Z-API.
    
    Z-API expects international format without symbols: DDI + DDD + NUMBER
    Example: 5511999999999
    
    Args:
        phone: Phone number (can include symbols, will be stripped)
        
    Returns:
        Formatted phone number (only digits)
        
    Raises:
        ValidationError: If phone number is invalid
    """
    # Convert to string and remove all non-digit characters
    phone_str = str(phone)
    digits_only = re.sub(r'\D', '', phone_str)
    
    if not digits_only:
        raise ValidationError("Phone number cannot be empty")
    
    if len(digits_only) < 10:
        raise ValidationError(f"Phone number too short: {digits_only}")
    
    return digits_only


def is_group_id(chat_id: str) -> bool:
    """
    Check if chat ID is a group ID.
    
    Group IDs have two formats:
    - Old: {number}-{timestamp} (e.g., "5511999999999-1623281429")
    - New: {id}-group (e.g., "120363019502650977-group")
    
    Args:
        chat_id: Chat or group ID
        
    Returns:
        True if group ID, False otherwise
    """
    return '-group' in chat_id or (
        '-' in chat_id and not chat_id.endswith('-group') and '@' not in chat_id
    )


def encode_base64(file_path: str | Path) -> str:
    """
    Encode file to base64 string with proper prefix for Z-API.
    
    Args:
        file_path: Path to file
        
    Returns:
        Base64 string with data URI prefix
        
    Raises:
        ValidationError: If file doesn't exist or can't be read
    """
    path = Path(file_path)
    
    if not path.exists():
        raise ValidationError(f"File not found: {file_path}")
    
    if not path.is_file():
        raise ValidationError(f"Not a file: {file_path}")
    
    try:
        with open(path, 'rb') as f:
            file_bytes = f.read()
        
        # Encode to base64
        b64_string = base64.b64encode(file_bytes).decode('utf-8')
        
        # Get mime type
        mime_type = get_mime_type(path)
        
        # Return with data URI prefix
        return f"data:{mime_type};base64,{b64_string}"
    
    except Exception as e:
        raise ValidationError(f"Failed to encode file: {e}")


def get_mime_type(file_path: str | Path) -> str:
    """
    Get MIME type for file.
    
    Args:
        file_path: Path to file
        
    Returns:
        MIME type string
    """
    path = Path(file_path)
    mime_type, _ = mimetypes.guess_type(str(path))
    
    if mime_type:
        return mime_type
    
    # Fallback based on extension
    extension = path.suffix.lower()
    mime_map = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.mp4': 'video/mp4',
        '.mp3': 'audio/mpeg',
        '.ogg': 'audio/ogg',
        '.wav': 'audio/wav',
        '.pdf': 'application/pdf',
        '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.xls': 'application/vnd.ms-excel',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    }
    
    return mime_map.get(extension, 'application/octet-stream')


def is_url(value: str) -> bool:
    """
    Check if string is a valid URL.
    
    Args:
        value: String to check
        
    Returns:
        True if valid URL, False otherwise
    """
    try:
        result = urlparse(value)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def is_base64(value: str) -> bool:
    """
    Check if string is base64 encoded (with data URI prefix).
    
    Args:
        value: String to check
        
    Returns:
        True if base64 data URI, False otherwise
    """
    return value.startswith('data:') and ';base64,' in value


def format_text_markdown(
    text: str,
    bold: bool = False,
    italic: bool = False,
    strikethrough: bool = False,
    monospace: bool = False
) -> str:
    """
    Format text with WhatsApp markdown.
    
    Args:
        text: Text to format
        bold: Make text bold
        italic: Make text italic
        strikethrough: Add strikethrough
        monospace: Use monospace font
        
    Returns:
        Formatted text
    """
    if bold:
        text = f"*{text}*"
    if italic:
        text = f"_{text}_"
    if strikethrough:
        text = f"~{text}~"
    if monospace:
        text = f"```{text}```"
    
    return text


def validate_phone_list(phones: list[str | int]) -> list[str]:
    """
    Validate and format a list of phone numbers.
    
    Args:
        phones: List of phone numbers
        
    Returns:
        List of formatted phone numbers
        
    Raises:
        ValidationError: If any phone number is invalid
    """
    if not phones:
        raise ValidationError("Phone list cannot be empty")
    
    formatted = []
    for phone in phones:
        formatted.append(format_phone(phone))
    
    return formatted


def build_request_body(**kwargs: Any) -> dict[str, Any]:
    """
    Build request body by removing None values.
    
    Args:
        **kwargs: Request parameters
        
    Returns:
        Cleaned request body
    """
    return {k: v for k, v in kwargs.items() if v is not None}
