"""Message types for received webhooks."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Literal
from datetime import datetime


@dataclass
class BaseWebhookMessage:
    """
    Base class for all webhook messages.
    
    Common fields across all message types.
    """
    # Message metadata
    message_id: str
    instance_id: str
    phone: str
    from_me: bool
    moment: int  # Timestamp in milliseconds
    status: str  # PENDING, SENT, RECEIVED, READ, PLAYED
    type: str  # ReceivedCallback, etc.
    
    # Chat info
    chat_name: str | None = None
    is_group: bool = False
    is_newsletter: bool = False
    is_status_reply: bool = False
    
    # Sender info
    sender_name: str | None = None
    sender_photo: str | None = None
    sender_lid: str | None = None
    photo: str | None = None
    
    # Group-specific
    participant_phone: str | None = None
    participant_lid: str | None = None
    
    # Other flags
    connected_phone: str | None = None
    waiting_message: bool = False
    is_edit: bool = False
    broadcast: bool = False
    forwarded: bool = False
    from_api: bool = False
    
    # Optional fields
    reference_message_id: str | None = None  # For replies
    message_expiration_seconds: int | None = None
    
    # Raw data for debugging
    _raw: dict[str, Any] = field(default_factory=dict, repr=False)
    
    @property
    def timestamp(self) -> datetime:
        """Convert moment (milliseconds) to datetime."""
        return datetime.fromtimestamp(self.moment / 1000)
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BaseWebhookMessage:
        """Create from webhook payload."""
        return cls(
            message_id=data.get('messageId', ''),
            instance_id=data.get('instanceId', ''),
            phone=data.get('phone', ''),
            from_me=data.get('fromMe', False),
            moment=data.get('momment', data.get('moment', 0)),  # Note: API uses 'momment'
            status=data.get('status', 'UNKNOWN'),
            type=data.get('type', 'ReceivedCallback'),
            chat_name=data.get('chatName'),
            is_group=data.get('isGroup', False),
            is_newsletter=data.get('isNewsletter', False),
            is_status_reply=data.get('isStatusReply', False),
            sender_name=data.get('senderName'),
            sender_photo=data.get('senderPhoto'),
            sender_lid=data.get('senderLid'),
            photo=data.get('photo'),
            participant_phone=data.get('participantPhone'),
            participant_lid=data.get('participantLid'),
            connected_phone=data.get('connectedPhone'),
            waiting_message=data.get('waitingMessage', False),
            is_edit=data.get('isEdit', False),
            broadcast=data.get('broadcast', False),
            forwarded=data.get('forwarded', False),
            from_api=data.get('fromApi', False),
            reference_message_id=data.get('referenceMessageId'),
            message_expiration_seconds=data.get('messageExpirationSeconds'),
            _raw=data,
        )


@dataclass
class TextMessage(BaseWebhookMessage):
    """Text message received via webhook."""
    
    message: str = ""
    description: str | None = None
    title: str | None = None
    url: str | None = None
    thumbnail_url: str | None = None
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TextMessage:
        """Create from webhook payload."""
        base = super().from_dict(data)
        text_data = data.get('text', {})
        
        return cls(
            **{k: v for k, v in base.__dict__.items() if not k.startswith('_')},
            message=text_data.get('message', ''),
            description=text_data.get('description') or text_data.get('descritpion'),  # API typo
            title=text_data.get('title'),
            url=text_data.get('url'),
            thumbnail_url=text_data.get('thumbnailUrl'),
            _raw=data,
        )


@dataclass
class ImageMessage(BaseWebhookMessage):
    """Image message received via webhook."""
    
    image_url: str = ""
    thumbnail_url: str | None = None
    caption: str | None = None
    mime_type: str | None = None
    width: int | None = None
    height: int | None = None
    view_once: bool = False
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ImageMessage:
        """Create from webhook payload."""
        base = super().from_dict(data)
        image_data = data.get('image', {})
        
        return cls(
            **{k: v for k, v in base.__dict__.items() if not k.startswith('_')},
            image_url=image_data.get('imageUrl', ''),
            thumbnail_url=image_data.get('thumbnailUrl'),
            caption=image_data.get('caption'),
            mime_type=image_data.get('mimeType'),
            width=image_data.get('width'),
            height=image_data.get('height'),
            view_once=image_data.get('viewOnce', False),
            _raw=data,
        )


@dataclass
class VideoMessage(BaseWebhookMessage):
    """Video message received via webhook."""
    
    video_url: str = ""
    caption: str | None = None
    mime_type: str | None = None
    seconds: int | None = None
    view_once: bool = False
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VideoMessage:
        """Create from webhook payload."""
        base = super().from_dict(data)
        video_data = data.get('video', {})
        
        return cls(
            **{k: v for k, v in base.__dict__.items() if not k.startswith('_')},
            video_url=video_data.get('videoUrl', ''),
            caption=video_data.get('caption'),
            mime_type=video_data.get('mimeType'),
            seconds=video_data.get('seconds'),
            view_once=video_data.get('viewOnce', False),
            _raw=data,
        )


@dataclass
class AudioMessage(BaseWebhookMessage):
    """Audio message received via webhook."""
    
    audio_url: str = ""
    mime_type: str | None = None
    seconds: int | None = None
    ptt: bool = False  # Push-to-talk (voice message)
    view_once: bool = False
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AudioMessage:
        """Create from webhook payload."""
        base = super().from_dict(data)
        audio_data = data.get('audio', {})
        
        return cls(
            **{k: v for k, v in base.__dict__.items() if not k.startswith('_')},
            audio_url=audio_data.get('audioUrl', ''),
            mime_type=audio_data.get('mimeType'),
            seconds=audio_data.get('seconds'),
            ptt=audio_data.get('ptt', False),
            view_once=audio_data.get('viewOnce', False),
            _raw=data,
        )


@dataclass
class DocumentMessage(BaseWebhookMessage):
    """Document message received via webhook."""
    
    document_url: str = ""
    file_name: str | None = None
    title: str | None = None
    page_count: str | None = None
    mime_type: str | None = None
    thumbnail_url: str | None = None
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> DocumentMessage:
        """Create from webhook payload."""
        base = super().from_dict(data)
        doc_data = data.get('document', {})
        
        return cls(
            **{k: v for k, v in base.__dict__.items() if not k.startswith('_')},
            document_url=doc_data.get('documentUrl', ''),
            file_name=doc_data.get('fileName'),
            title=doc_data.get('title'),
            page_count=doc_data.get('pageCount'),
            mime_type=doc_data.get('mimeType'),
            thumbnail_url=doc_data.get('thumbnailUrl'),
            _raw=data,
        )


@dataclass
class StickerMessage(BaseWebhookMessage):
    """Sticker message received via webhook."""
    
    sticker_url: str = ""
    mime_type: str | None = None
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StickerMessage:
        """Create from webhook payload."""
        base = super().from_dict(data)
        sticker_data = data.get('sticker', {})
        
        return cls(
            **{k: v for k, v in base.__dict__.items() if not k.startswith('_')},
            sticker_url=sticker_data.get('stickerUrl', ''),
            mime_type=sticker_data.get('mimeType'),
            _raw=data,
        )


@dataclass
class LocationMessage(BaseWebhookMessage):
    """Location message received via webhook."""
    
    latitude: float = 0.0
    longitude: float = 0.0
    name: str | None = None
    address: str | None = None
    url: str | None = None
    thumbnail_url: str | None = None
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LocationMessage:
        """Create from webhook payload."""
        base = super().from_dict(data)
        loc_data = data.get('location', {})
        
        return cls(
            **{k: v for k, v in base.__dict__.items() if not k.startswith('_')},
            latitude=loc_data.get('latitude', 0.0),
            longitude=loc_data.get('longitude', 0.0),
            name=loc_data.get('name'),
            address=loc_data.get('address'),
            url=loc_data.get('url'),
            thumbnail_url=loc_data.get('thumbnailUrl'),
            _raw=data,
        )


@dataclass
class ContactMessage(BaseWebhookMessage):
    """Contact message received via webhook."""
    
    display_name: str = ""
    vcard: str = ""
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ContactMessage:
        """Create from webhook payload."""
        base = super().from_dict(data)
        contact_data = data.get('contact', {})
        
        return cls(
            **{k: v for k, v in base.__dict__.items() if not k.startswith('_')},
            display_name=contact_data.get('displayName', ''),
            vcard=contact_data.get('vCard', ''),
            _raw=data,
        )


@dataclass
class ReferencedMessage:
    """Referenced message info (for reactions)."""
    message_id: str
    from_me: bool
    phone: str
    participant: str | None = None


@dataclass
class ReactionMessage(BaseWebhookMessage):
    """Reaction message received via webhook."""
    
    emoji: str = ""
    reaction_time: int = 0
    reaction_by: str = ""
    referenced_message: ReferencedMessage | None = None
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ReactionMessage:
        """Create from webhook payload."""
        base = super().from_dict(data)
        reaction_data = data.get('reaction', {})
        
        ref_msg = None
        if ref_data := reaction_data.get('referencedMessage'):
            ref_msg = ReferencedMessage(
                message_id=ref_data.get('messageId', ''),
                from_me=ref_data.get('fromMe', False),
                phone=ref_data.get('phone', ''),
                participant=ref_data.get('participant'),
            )
        
        return cls(
            **{k: v for k, v in base.__dict__.items() if not k.startswith('_')},
            emoji=reaction_data.get('value', ''),
            reaction_time=reaction_data.get('time', 0),
            reaction_by=reaction_data.get('reactionBy', ''),
            referenced_message=ref_msg,
            _raw=data,
        )


# Type alias for any message type
WebhookMessage = (
    TextMessage 
    | ImageMessage 
    | VideoMessage 
    | AudioMessage 
    | DocumentMessage 
    | StickerMessage 
    | LocationMessage 
    | ContactMessage 
    | ReactionMessage
    | BaseWebhookMessage
)
