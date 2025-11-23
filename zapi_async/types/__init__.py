"""Type definitions for zapi_async."""

from .sent import SentMessage
from .instance import InstanceStatus, QRCode, PhoneCode
from .group import GroupCreated, GroupMetadata, GroupParticipant, GroupInviteInfo
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
from .webhook import (
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

__all__ = [
    # Sent messages
    'SentMessage',
    
    # Instance
    'InstanceStatus',
    'QRCode',
    'PhoneCode',
    
    # Groups
    'GroupCreated',
    'GroupMetadata',
    'GroupParticipant',
    'GroupInviteInfo',
    
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
]
