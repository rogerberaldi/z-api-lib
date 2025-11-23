"""
🚀 Z-API Async - Build WhatsApp Bots with Z-API in Python

An async Python library for Z-API WhatsApp service.

Example:
    >>> from zapi_async import ZAPIClient
    >>> 
    >>> async def main():
    ...     client = ZAPIClient(
    ...         instance_id="YOUR_INSTANCE",
    ...         token="YOUR_TOKEN",
    ...         client_token="YOUR_CLIENT_TOKEN"
    ...     )
    ...     
    ...     # Send a message
    ...     result = await client.send_text(
    ...         phone="5511999999999",
    ...         message="Hello from Z-API!"
    ...     )
    ...     print(f"Message sent: {result.message_id}")
    ...     
    ...     await client.close()
"""

from .client import ZAPIClient
from .errors import (
    ZAPIError,
    AuthenticationError,
    InstanceError,
    RateLimitError,
    MessageError,
    WebhookError,
    ValidationError,
    MediaError,
    GroupError,
    NetworkError,
)
from .types import (
    SentMessage,
    InstanceStatus,
    QRCode,
    PhoneCode,
    # Webhook messages
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
    # Webhook parsing
    parse_webhook_message,
    is_text_message,
    is_media_message,
    is_image_message,
    is_video_message,
    is_audio_message,
    is_document_message,
    is_sticker_message,
    is_location_message,
    is_contact_message,
    is_reaction_message,
    is_group_message,
    is_from_me,
)
from .utils import __version__, __author__, __license__

__all__ = [
    # Main client
    'ZAPIClient',
    
    # Exceptions
    'ZAPIError',
    'AuthenticationError',
    'InstanceError',
    'RateLimitError',
    'MessageError',
    'WebhookError',
    'ValidationError',
    'MediaError',
    'GroupError',
    'NetworkError',
    
    # Sent messages
    'SentMessage',
    
    # Instance
    'InstanceStatus',
    'QRCode',
    'PhoneCode',
    
    # Received messages
    'BaseWebhookMessage',
    'TextMessage',
    'ImageMessage',
    'VideoMessage',
    'AudioMessage',
    'DocumentMessage',
    'StickerMessage',
    'LocationMessage',
    'ContactMessage',
    'ReactionMessage',
    'WebhookMessage',
    
    # Webhook parsing
    'parse_webhook_message',
    'is_text_message',
    'is_media_message',
    'is_image_message',
    'is_video_message',
    'is_audio_message',
    'is_document_message',
    'is_sticker_message',
    'is_location_message',
    'is_contact_message',
    'is_reaction_message',
    'is_group_message',
    'is_from_me',
    
    # Metadata
    '__version__',
    '__author__',
    '__license__',
]
