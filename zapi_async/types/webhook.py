"""Webhook payload parsing and handling."""

from __future__ import annotations
from typing import Any
from .message import (
    BaseWebhookMessage,
    TextMessage,
    ImageMessage,
    VideoMessage,
    AudioMessage,
    DocumentMessage,
    StickerMessage,
    LocationMessage,
    ContactMessage,
    ReactionMessage,
    WebhookMessage,
)


def parse_webhook_message(payload: dict[str, Any]) -> WebhookMessage:
    """
    Parse webhook payload into appropriate message type.
    
    Automatically detects the message type based on payload structure
    and returns the correct typed message object.
    
    Args:
        payload: Raw webhook JSON payload
        
    Returns:
        Typed message object (TextMessage, ImageMessage, etc.)
        
    Example:
        >>> payload = {
        ...     "type": "ReceivedCallback",
        ...     "messageId": "ABC123",
        ...     "phone": "5511999999999",
        ...     "text": {"message": "Hello!"}
        ... }
        >>> msg = parse_webhook_message(payload)
        >>> isinstance(msg, TextMessage)
        True
        >>> msg.message
        'Hello!'
    """
    # Check for specific message types by presence of data fields
    
    if 'reaction' in payload:
        return ReactionMessage.from_dict(payload)
    
    if 'text' in payload:
        return TextMessage.from_dict(payload)
    
    if 'image' in payload:
        return ImageMessage.from_dict(payload)
    
    if 'video' in payload:
        return VideoMessage.from_dict(payload)
    
    if 'audio' in payload:
        return AudioMessage.from_dict(payload)
    
    if 'document' in payload:
        return DocumentMessage.from_dict(payload)
    
    if 'sticker' in payload:
        return StickerMessage.from_dict(payload)
    
    if 'location' in payload:
        return LocationMessage.from_dict(payload)
    
    if 'contact' in payload:
        return ContactMessage.from_dict(payload)
    
    # Fallback to base message
    return BaseWebhookMessage.from_dict(payload)


def is_text_message(msg: WebhookMessage) -> bool:
    """Check if message is a text message."""
    return isinstance(msg, TextMessage)


def is_media_message(msg: WebhookMessage) -> bool:
    """Check if message is a media message (image, video, audio, document, sticker)."""
    return isinstance(msg, (ImageMessage, VideoMessage, AudioMessage, DocumentMessage, StickerMessage))


def is_image_message(msg: WebhookMessage) -> bool:
    """Check if message is an image."""
    return isinstance(msg, ImageMessage)


def is_video_message(msg: WebhookMessage) -> bool:
    """Check if message is a video."""
    return isinstance(msg, VideoMessage)


def is_audio_message(msg: WebhookMessage) -> bool:
    """Check if message is audio."""
    return isinstance(msg, AudioMessage)


def is_document_message(msg: WebhookMessage) -> bool:
    """Check if message is a document."""
    return isinstance(msg, DocumentMessage)


def is_sticker_message(msg: WebhookMessage) -> bool:
    """Check if message is a sticker."""
    return isinstance(msg, StickerMessage)


def is_location_message(msg: WebhookMessage) -> bool:
    """Check if message is a location."""
    return isinstance(msg, LocationMessage)


def is_contact_message(msg: WebhookMessage) -> bool:
    """Check if message is a contact."""
    return isinstance(msg, ContactMessage)


def is_reaction_message(msg: WebhookMessage) -> bool:
    """Check if message is a reaction."""
    return isinstance(msg, ReactionMessage)


def is_group_message(msg: WebhookMessage) -> bool:
    """Check if message is from a group."""
    return msg.is_group


def is_from_me(msg: WebhookMessage) -> bool:
    """Check if message was sent by me (the connected number)."""
    return msg.from_me
