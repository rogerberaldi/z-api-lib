"""Main Z-API async client."""

from __future__ import annotations
import logging
from pathlib import Path
from typing import Any
import httpx

from .api import GraphAPI
from .errors import ValidationError
from ._helpers import (
    format_phone,
    is_url,
    is_base64,
    encode_base64,
    build_request_body,
)
from .types import SentMessage, InstanceStatus, QRCode, PhoneCode

_logger = logging.getLogger(__name__)


class ZAPIClient:
    """
    Z-API Async WhatsApp Client.
    
    This is the main client for interacting with Z-API.
    
    Example:
        >>> from zapi_async import ZAPIClient
        >>> 
        >>> client = ZAPIClient(
        ...     instance_id="YOUR_INSTANCE",
        ...     token="YOUR_TOKEN",
        ...     client_token="YOUR_CLIENT_TOKEN"  # Optional
        ... )
        >>> 
        >>> # Send a text message
        >>> result = await client.send_text(
        ...     phone="5511999999999",
        ...     message="Hello from Z-API!"
        ... )
        >>> print(result.message_id)
    """
    
    def __init__(
        self,
        instance_id: str,
        token: str,
        client_token: str | None = None,
        session: httpx.AsyncClient | None = None,
    ):
        """
        Initialize Z-API client.
        
        Args:
            instance_id: Z-API instance ID
            token: Z-API token
            client_token: Optional security client token (recommended)
            session: Optional httpx AsyncClient (for custom configuration)
        """
        self.instance_id = instance_id
        self.token = token
        self.client_token = client_token
        self.api = GraphAPI(
            instance_id=instance_id,
            token=token,
            client_token=client_token,
            session=session,
        )
    
    def __repr__(self) -> str:
        return f"ZAPIClient(instance_id='{self.instance_id}')"
    
    # ========== Instance Management ==========
    
    async def get_status(self) -> InstanceStatus:
        """
        Get instance connection status.
        
        Returns:
            Instance status with connection info
            
        Example:
            >>> status = await client.get_status()
            >>> if status.connected:
            ...     print(f"Connected as {status.phone}")
        """
        data = await self.api.get("status")
        return InstanceStatus.from_dict(data)
    
    async def get_qrcode(self, image: bool = False) -> QRCode:
        """
        Get QR code for connecting instance.
        
        Args:
            image: If True, get base64 image; if False, get raw QR code value
            
        Returns:
            QR code data
            
        Note:
            QR codes expire every 20 seconds. You should refresh periodically.
            
        Example:
            >>> qr = await client.get_qrcode(image=True)
            >>> # Display qr.image in your UI
        """
        endpoint = "qr-code/image" if image else "qr-code"
        data = await self.api.get(endpoint)
        return QRCode.from_dict(data)
    
    async def get_phone_code(self, phone: str | int) -> PhoneCode:
        """
        Get phone code for connection without QR code.
        
        Args:
            phone: Phone number to connect
            
        Returns:
            Phone code for connection
            
        Example:
            >>> code = await client.get_phone_code("5511999999999")
            >>> # User enters code.code in WhatsApp
        """
        phone_formatted = format_phone(phone)
        data = await self.api.get(f"phone-code/{phone_formatted}")
        return PhoneCode.from_dict(data)
    
    async def disconnect(self) -> dict[str, Any]:
        """
        Disconnect instance.
        
        Returns:
            Disconnect response
        """
        return await self.api.post("disconnect")
    
    # ========== Message Sending - Text ==========
    
    async def send_text(
        self,
        phone: str | int,
        message: str,
        *,
        delay_message: int | None = None,
        delay_typing: int | None = None,
        edit_message_id: str | None = None,
    ) -> SentMessage:
        """
        Send text message.
        
        Args:
            phone: Phone number or group ID
            message: Text message (supports WhatsApp formatting: *bold*, _italic_, ~strikethrough~, ```monospace```)
            delay_message: Delay before sending (1-15 seconds)
            delay_typing: Show "typing..." status duration (1-15 seconds)
            edit_message_id: Message ID to edit (requires webhook configuration)
            
        Returns:
            Sent message info
            
        Example:
            >>> result = await client.send_text(
            ...     phone="5511999999999",
            ...     message="Hello! *This is bold* and _this is italic_"
            ... )
        """
        body = build_request_body(
            phone=format_phone(phone),
            message=message,
            delayMessage=delay_message,
            delayTyping=delay_typing,
            editMessageId=edit_message_id,
        )
        
        data = await self.api.post("send-text", json=body)
        return SentMessage.from_dict(data)
    
    # ========== Message Sending - Media ==========
    
    async def send_image(
        self,
        phone: str | int,
        image: str | Path,
        *,
        caption: str | None = None,
        message_id: str | None = None,
        delay_message: int | None = None,
        view_once: bool = False,
    ) -> SentMessage:
        """
        Send image message.
        
        Args:
            phone: Phone number or group ID
            image: Image URL, base64 string, or file path
            caption: Optional image caption
            message_id: Message ID to reply to
            delay_message: Delay before sending (1-15 seconds)
            view_once: Send as view-once message
            
        Returns:
            Sent message info
            
        Example:
            >>> # Send from URL
            >>> result = await client.send_image(
            ...     phone="5511999999999",
            ...     image="https://example.com/image.jpg",
            ...     caption="Check this out!"
            ... )
            >>> 
            >>> # Send from file
            >>> result = await client.send_image(
            ...     phone="5511999999999",
            ...     image="/path/to/image.jpg"
            ... )
        """
        # Handle file path
        image_value = image
        if isinstance(image, Path) or (isinstance(image, str) and not is_url(image) and not is_base64(image)):
            image_value = encode_base64(image)
        
        body = build_request_body(
            phone=format_phone(phone),
            image=str(image_value),
            caption=caption,
            messageId=message_id,
            delayMessage=delay_message,
            viewOnce=view_once,
        )
        
        data = await self.api.post("send-image", json=body)
        return SentMessage.from_dict(data)
    
    async def send_video(
        self,
        phone: str | int,
        video: str | Path,
        *,
        caption: str | None = None,
        message_id: str | None = None,
        delay_message: int | None = None,
        view_once: bool = False,
    ) -> SentMessage:
        """
        Send video message.
        
        Args:
            phone: Phone number or group ID
            video: Video URL, base64 string, or file path
            caption: Optional video caption
            message_id: Message ID to reply to
            delay_message: Delay before sending (1-15 seconds)
            view_once: Send as view-once message
            
        Returns:
            Sent message info
        """
        video_value = video
        if isinstance(video, Path) or (isinstance(video, str) and not is_url(video) and not is_base64(video)):
            video_value = encode_base64(video)
        
        body = build_request_body(
            phone=format_phone(phone),
            video=str(video_value),
            caption=caption,
            messageId=message_id,
            delayMessage=delay_message,
            viewOnce=view_once,
        )
        
        data = await self.api.post("send-video", json=body)
        return SentMessage.from_dict(data)
    
    async def send_audio(
        self,
        phone: str | int,
        audio: str | Path,
        *,
        message_id: str | None = None,
        delay_message: int | None = None,
    ) -> SentMessage:
        """
        Send audio message.
        
        Args:
            phone: Phone number or group ID
            audio: Audio URL, base64 string, or file path
            message_id: Message ID to reply to
            delay_message: Delay before sending (1-15 seconds)
            
        Returns:
            Sent message info
        """
        audio_value = audio
        if isinstance(audio, Path) or (isinstance(audio, str) and not is_url(audio) and not is_base64(audio)):
            audio_value = encode_base64(audio)
        
        body = build_request_body(
            phone=format_phone(phone),
            audio=str(audio_value),
            messageId=message_id,
            delayMessage=delay_message,
        )
        
        data = await self.api.post("send-audio", json=body)
        return SentMessage.from_dict(data)
    
    async def send_document(
        self,
        phone: str | int,
        document: str | Path,
        *,
        filename: str | None = None,
        caption: str | None = None,
        message_id: str | None = None,
        delay_message: int | None = None,
    ) -> SentMessage:
        """
        Send document message.
        
        Args:
            phone: Phone number or group ID
            document: Document URL, base64 string, or file path
            filename: Optional filename
            caption: Optional caption
            message_id: Message ID to reply to
            delay_message: Delay before sending (1-15 seconds)
            
        Returns:
            Sent message info
        """
        document_value = document
        if isinstance(document, Path) or (isinstance(document, str) and not is_url(document) and not is_base64(document)):
            document_value = encode_base64(document)
            if not filename and isinstance(document, (str, Path)):
                filename = Path(document).name
        
        body = build_request_body(
            phone=format_phone(phone),
            document=str(document_value),
            fileName=filename,
            caption=caption,
            messageId=message_id,
            delayMessage=delay_message,
        )
        
        data = await self.api.post("send-document", json=body)
        return SentMessage.from_dict(data)
    
    async def send_sticker(
        self,
        phone: str | int,
        sticker: str | Path,
        *,
        message_id: str | None = None,
        delay_message: int | None = None,
    ) -> SentMessage:
        """
        Send sticker message.
        
        Args:
            phone: Phone number or group ID
            sticker: Sticker URL, base64 string, or file path
            message_id: Message ID to reply to
            delay_message: Delay before sending (1-15 seconds)
            
        Returns:
            Sent message info
            
        Note:
            - Static stickers: 512x512 pixels, max 100KB
            - Animated stickers: 512x512 pixels, max 500KB
        """
        sticker_value = sticker
        if isinstance(sticker, Path) or (isinstance(sticker, str) and not is_url(sticker) and not is_base64(sticker)):
            sticker_value = encode_base64(sticker)
        
        body = build_request_body(
            phone=format_phone(phone),
            sticker=str(sticker_value),
            messageId=message_id,
            delayMessage=delay_message,
        )
        
        data = await self.api.post("send-sticker", json=body)
        return SentMessage.from_dict(data)
    
    async def send_location(
        self,
        phone: str | int,
        latitude: float,
        longitude: float,
        *,
        name: str | None = None,
        address: str | None = None,
        url: str | None = None,
        message_id: str | None = None,
        delay_message: int | None = None,
    ) -> SentMessage:
        """
        Send location message.
        
        Args:
            phone: Phone number or group ID
            latitude: Location latitude
            longitude: Location longitude
            name: Optional location name
            address: Optional location address
            url: Optional location URL
            message_id: Message ID to reply to
            delay_message: Delay before sending (1-15 seconds)
            
        Returns:
            Sent message info
            
        Example:
            >>> result = await client.send_location(
            ...     phone="5511999999999",
            ...     latitude=-23.5505,
            ...     longitude=-46.6333,
            ...     name="São Paulo",
            ...     address="São Paulo, Brazil"
            ... )
        """
        body = build_request_body(
            phone=format_phone(phone),
            latitude=latitude,
            longitude=longitude,
            name=name,
            address=address,
            url=url,
            messageId=message_id,
            delayMessage=delay_message,
        )
        
        data = await self.api.post("send-location", json=body)
        return SentMessage.from_dict(data)
    
    async def send_contact(
        self,
        phone: str | int,
        contact_phone: str | int,
        contact_name: str,
        *,
        message_id: str | None = None,
        delay_message: int | None = None,
    ) -> SentMessage:
        """
        Send contact message.
        
        Args:
            phone: Phone number or group ID
            contact_phone: Contact's phone number
            contact_name: Contact's name
            message_id: Message ID to reply to
            delay_message: Delay before sending (1-15 seconds)
            
        Returns:
            Sent message info
            
        Example:
            >>> result = await client.send_contact(
            ...     phone="5511999999999",
            ...     contact_phone="5511888888888",
            ...     contact_name="John Doe"
            ... )
        """
        body = build_request_body(
            phone=format_phone(phone),
            contactPhone=format_phone(contact_phone),
            contactName=contact_name,
            messageId=message_id,
            delayMessage=delay_message,
        )
        
        data = await self.api.post("send-contact", json=body)
        return SentMessage.from_dict(data)
    
    async def send_link(
        self,
        phone: str | int,
        url: str,
        message: str,
        *,
        title: str | None = None,
        description: str | None = None,
        image: str | None = None,
        message_id: str | None = None,
        delay_message: int | None = None,
    ) -> SentMessage:
        """
        Send link preview message.
        
        Args:
            phone: Phone number or group ID
            url: URL to preview
            message: Message text
            title: Optional preview title
            description: Optional preview description
            image: Optional preview image URL
            message_id: Message ID to reply to
            delay_message: Delay before sending (1-15 seconds)
            
        Returns:
            Sent message info
            
        Example:
            >>> result = await client.send_link(
            ...     phone="5511999999999",
            ...     url="https://www.z-api.io",
            ...     message="Check out Z-API!",
            ...     title="Z-API - WhatsApp API"
            ... )
        """
        body = build_request_body(
            phone=format_phone(phone),
            message=message,
            url=url,
            title=title,
            description=description,
            image=image,
            messageId=message_id,
            delayMessage=delay_message,
        )
        
        data = await self.api.post("send-link", json=body)
        return SentMessage.from_dict(data)
    
    async def send_reaction(
        self,
        phone: str | int,
        message_id: str,
        emoji: str,
        *,
        delay_message: int | None = None,
    ) -> SentMessage:
        """
        Send emoji reaction to a message.
        
        Args:
            phone: Phone number or group ID
            message_id: Message ID to react to
            emoji: Emoji to react with (single emoji)
            delay_message: Delay before sending (1-15 seconds)
            
        Returns:
            Sent message info
            
        Example:
            >>> result = await client.send_reaction(
            ...     phone="5511999999999",
            ...     message_id="MESSAGE_ID",
            ...     emoji="❤️"
            ... )
        """
        body = build_request_body(
            phone=format_phone(phone),
            messageId=message_id,
            reaction=emoji,
            delayMessage=delay_message,
        )
        
        data = await self.api.post("send-reaction", json=body)
        return SentMessage.from_dict(data)
    
    async def remove_reaction(
        self,
        phone: str | int,
        message_id: str,
    ) -> SentMessage:
        """
        Remove reaction from a message.
        
        Args:
            phone: Phone number or group ID
            message_id: Message ID to remove reaction from
            
        Returns:
            Sent message info
        """
        body = build_request_body(
            phone=format_phone(phone),
            messageId=message_id,
        )
        
        data = await self.api.post("send-remove-reaction", json=body)
        return SentMessage.from_dict(data)
    
    # ========== Interactive Messages ==========
    
    async def send_button_list(
        self,
        phone: str | int,
        message: str,
        buttons: list[dict[str, str]],
        *,
        delay_message: int | None = None,
    ) -> SentMessage:
        """
        Send message with button list.
        
        Args:
            phone: Phone number or group ID
            message: Message text (cannot be empty)
            buttons: List of buttons, each with 'label' and optional 'id'
            delay_message: Delay before sending (1-15 seconds)
            
        Returns:
            Sent message info
            
        Example:
            >>> buttons = [
            ...     {"id": "1", "label": "Option 1"},
            ...     {"id": "2", "label": "Option 2"},
            ... ]
            >>> result = await client.send_button_list(
            ...     phone="5511999999999",
            ...     message="Choose an option:",
            ...     buttons=buttons
            ... )
        """
        body = build_request_body(
            phone=format_phone(phone),
            message=message,
            buttonList={"buttons": buttons},
            delayMessage=delay_message,
        )
        
        data = await self.api.post("send-button-list", json=body)
        return SentMessage.from_dict(data)
    
    async def send_option_list(
        self,
        phone: str | int,
        message: str,
        title: str,
        button_label: str,
        options: list[dict[str, str]],
        *,
        delay_message: int | None = None,
    ) -> SentMessage:
        """
        Send message with option list.
        
        Args:
            phone: Phone number or group ID
            message: Message text
            title: List title
            button_label: Text for button that opens the list
            options: List of options, each with 'title', 'description', and optional 'id'
            delay_message: Delay before sending (1-15 seconds)
            
        Returns:
            Sent message info
            
        Example:
            >>> options = [
            ...     {"id": "1", "title": "Z-API", "description": "Best WhatsApp API"},
            ...     {"id": "2", "title": "Others", "description": "Don't work"},
            ... ]
            >>> result = await client.send_option_list(
            ...     phone="5511999999999",
            ...     message="Select the best option:",
            ...     title="Available options",
            ...     button_label="Open options",
            ...     options=options
            ... )
        """
        body = build_request_body(
            phone=format_phone(phone),
            message=message,
            optionList={
                "title": title,
                "buttonLabel": button_label,
                "options": options
            },
            delayMessage=delay_message,
        )
        
        data = await self.api.post("send-option-list", json=body)
        return SentMessage.from_dict(data)
    
    async def send_poll(
        self,
        phone: str | int,
        message: str,
        options: list[str],
        *,
        max_options: int | None = None,
        delay_message: int | None = None,
    ) -> SentMessage:
        """
        Send poll message.
        
        Args:
            phone: Phone number or group ID
            message: Poll question
            options: List of poll option names
            max_options: Maximum votes per person (None = multiple choice, 1 = single choice)
            delay_message: Delay before sending (1-15 seconds)
            
        Returns:
            Sent message info
            
        Example:
            >>> # Multiple choice poll
            >>> result = await client.send_poll(
            ...     phone="5511999999999",
            ...     message="What's the best WhatsApp API?",
            ...     options=["Z-API", "Others"]
            ... )
            >>> 
            >>> # Single choice poll
            >>> result = await client.send_poll(
            ...     phone="5511999999999",
            ...     message="Choose one:",
            ...     options=["Option A", "Option B", "Option C"],
            ...     max_options=1
            ... )
        """
        # Convert string list to poll format
        poll_items = [{"name": option} for option in options]
        
        body = build_request_body(
            phone=format_phone(phone),
            message=message,
            poll=poll_items,
            pollMaxOptions=max_options,
            delayMessage=delay_message,
        )
        
        data = await self.api.post("send-poll", json=body)  
        return SentMessage.from_dict(data)
    
    
    
    # ========== Groups ==========
    
    async def create_group(
        self,
        group_name: str,
        phones: list[str | int],
        *,
        auto_invite: bool = True,
    ) -> "GroupCreated":
        """
        Create a WhatsApp group.
        
        Args:
            group_name: Name for the new group
            phones: List of participant phone numbers (minimum 1)
            auto_invite: Send private invite link to contacts not added
            
        Returns:
            GroupCreated with group_id and invite_link
            
        Note:
            - Do NOT include the connected number in phones list
            - Need at least 1 contact to create a group
            - If auto_invite=True, sends invite links to failed additions
            
        Example:
            >>> result = await client.create_group(
            ...     group_name="My Group",
            ...     phones=["5511999999999", "5511888888888"],
            ...     auto_invite=True
            ... )
            >>> print(f"Group created: {result.group_id}")
        """
        from .types.group import GroupCreated
        
        # Format all phones
        formatted_phones = [format_phone(p) for p in phones]
        
        body = build_request_body(
            groupName=group_name,
            phones=formatted_phones,
            autoInvite=auto_invite
        )
        
        data = await self.api.post("create-group", json=body)
        return GroupCreated.from_dict(data)
    
    async def get_group_metadata(self, group_id: str) -> "GroupMetadata":
        """
        Get complete group metadata.
        
        Args:
            group_id: Group ID (format: xxxxx-group or phone-timestamp)
            
        Returns:
            GroupMetadata with all group information
            
        Example:
            >>> metadata = await client.get_group_metadata("120363019502650977-group")
            >>> print(f"Group: {metadata.subject}")
            >>> print(f"Participants: {metadata.size}")
            >>> for p in metadata.participants:
            ...     print(f"  - {p.phone} (admin={p.is_admin})")
        """
        from .types.group import GroupMetadata
        
        body = build_request_body(groupId=group_id)
        data = await self.api.post("group-metadata", json=body)
        return GroupMetadata.from_dict(data)
    
    async def add_participant(
        self,
        group_id: str,
        phone: str | int,
        *,
        auto_invite: bool = True
    ) -> dict:
        """
        Add participant to group.
        
        Args:
            group_id: Group ID
            phone: Phone number to add
            auto_invite: Send invite link if can't add directly
            
        Returns:
            Response dict
            
        Example:
            >>> await client.add_participant(
            ...     "120363019502650977-group",
            ...     "5511999999999"
            ... )
        """
        body = build_request_body(
            groupId=group_id,
            phone=format_phone(phone),
            autoInvite=auto_invite
        )
        
        return await self.api.post("add-participant", json=body)
    
    async def remove_participant(
        self,
        group_id: str,
        phone: str | int
    ) -> dict:
        """
        Remove participant from group.
        
        Args:
            group_id: Group ID
            phone: Phone number to remove
            
        Returns:
            Response dict
            
        Example:
            >>> await client.remove_participant(
            ...     "120363019502650977-group",
            ...     "5511999999999"
            ... )
        """
        body = build_request_body(
            groupId=group_id,
            phone=format_phone(phone)
        )
        
        return await self.api.post("remove-participant", json=body)
    
    async def promote_to_admin(
        self,
        group_id: str,
        phone: str | int
    ) -> dict:
        """
        Promote participant to admin.
        
        Args:
            group_id: Group ID
            phone: Phone number to promote
            
        Returns:
            Response dict
            
        Example:
            >>> await client.promote_to_admin(
            ...     "120363019502650977-group",
            ...     "5511999999999"
            ... )
        """
        body = build_request_body(
            groupId=group_id,
            phone=format_phone(phone)
        )
        
        return await self.api.post("promote-participant", json=body)
    
    async def demote_admin(
        self,
        group_id: str,
        phone: str | int
    ) -> dict:
        """
        Demote admin to regular participant.
        
        Args:
            group_id: Group ID
            phone: Phone number to demote
            
        Returns:
            Response dict
            
        Example:
            >>> await client.demote_admin(
            ...     "120363019502650977-group",
            ...     "5511999999999"
            ... )
        """
        body = build_request_body(
            groupId=group_id,
            phone=format_phone(phone)
        )
        
        return await self.api.post("demote-participant", json=body)
    
    async def update_group_name(
        self,
        group_id: str,
        group_name: str
    ) -> dict:
        """
        Update group name/subject.
        
        Args:
            group_id: Group ID
            group_name: New group name
            
        Returns:
            Response dict
            
        Example:
            >>> await client.update_group_name(
            ...     "120363019502650977-group",
            ...     "New Group Name"
            ... )
        """
        body = build_request_body(
            groupId=group_id,
            groupName=group_name
        )
        
        return await self.api.post("update-group-name", json=body)
    
    async def update_group_description(
        self,
        group_id: str,
        description: str
    ) -> dict:
        """
        Update group description.
        
        Args:
            group_id: Group ID
            description: New group description
            
        Returns:
            Response dict
            
        Example:
            >>> await client.update_group_description(
            ...     "120363019502650977-group",
            ...     "This is our group description"
            ... )
        """
        body = build_request_body(
            groupId=group_id,
            description=description
        )
        
        return await self.api.post("update-group-description", json=body)
    
    async def update_group_photo(
        self,
        group_id: str,
        photo: str | Path
    ) -> dict:
        """
        Update group photo.
        
        Args:
            group_id: Group ID
            photo: Photo URL, base64, or file path
            
        Returns:
            Response dict
            
        Example:
            >>> # From URL
            >>> await client.update_group_photo(
            ...     "120363019502650977-group",
            ...     "https://example.com/group.jpg"
            ... )
            >>> 
            >>> # From file
            >>> await client.update_group_photo(
            ...     "120363019502650977-group",
            ...     "/path/to/photo.jpg"
            ... )
        """
        # Handle file path
        photo_value = photo
        if isinstance(photo, Path) or (isinstance(photo, str) and not is_url(photo) and not is_base64(photo)):
            photo_value = encode_base64(photo)
        
        body = build_request_body(
            groupId=group_id,
            photo=str(photo_value)
        )
        
        return await self.api.post("update-group-photo", json=body)
    
    async def leave_group(self, group_id: str) -> dict:
        """
        Leave a group.
        
        Args:
            group_id: Group ID
            
        Returns:
            Response dict
            
        Example:
            >>> await client.leave_group("120363019502650977-group")
        """
        body = build_request_body(groupId=group_id)
        return await self.api.post("leave-group", json=body)
    
    async def get_group_invite_link(self, group_id: str) -> "GroupInviteInfo":
        """
        Get group invitation link.
        
        Args:
            group_id: Group ID
            
        Returns:
            GroupInviteInfo with invite code and link
            
        Example:
            >>> invite = await client.get_group_invite_link("120363019502650977-group")
            >>> print(f"Invite link: {invite.invite_link}")
        """
        from .types.group import GroupInviteInfo
        
        body = build_request_body(groupId=group_id)
        data = await self.api.post("group-invite-link", json=body)
        return GroupInviteInfo.from_dict(data)
    
    async def accept_group_invite(self, invite_code: str) -> dict:
        """
        Accept group invitation.
        
        Args:
            invite_code: Group invitation code (from invite link)
            
        Returns:
            Response dict
            
        Example:
            >>> # From link: https://chat.whatsapp.com/ABC123DEF456
            >>> await client.accept_group_invite("ABC123DEF456")
        """
        body = build_request_body(inviteCode=invite_code)
        return await self.api.post("accept-group-invite", json=body)
    
    async def update_group_settings(
        self,
        group_id: str,
        *,
        only_admins_can_send: bool | None = None,
        only_admins_can_edit_info: bool | None = None
    ) -> dict:
        """
        Update group settings.
        
        Args:
            group_id: Group ID
            only_admins_can_send: Restrict sending messages to admins only
            only_admins_can_edit_info: Restrict editing group info to admins only
            
        Returns:
            Response dict
            
        Example:
            >>> # Lock group - only admins can send
            >>> await client.update_group_settings(
            ...     "120363019502650977-group",
            ...     only_admins_can_send=True
            ... )
        """
        body = build_request_body(
            groupId=group_id,
            onlyAdminsCanSend=only_admins_can_send,
            onlyAdminsCanEditInfo=only_admins_can_edit_info
        )
        
        return await self.api.post("update-group-settings", json=body)
    
    async def get_groups(self) -> list[dict]:
        """
        Get list of all groups.
        
        Returns:
            List of group objects
            
        Example:
            >>> groups = await client.get_groups()
            >>> for group in groups:
            ...     print(f"Group: {group['name']} - {group['id']}")
        """
        return await self.api.get("groups")
    
    
    # ========== Cleanup ==========
    
    async def close(self) -> None:
        """Close the client and cleanup resources."""
        await self.api.close()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
