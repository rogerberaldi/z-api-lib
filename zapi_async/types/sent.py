"""Sent message response types."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass
class SentMessage:
    """
    Response when a message is sent successfully.
    
    Attributes:
        zaap_id: Z-API internal message ID
        message_id: WhatsApp message ID
        id: Compatibility ID (same as message_id, for Zapier)
    """
    zaap_id: str
    message_id: str
    id: str
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SentMessage:
        """
        Create from API response.
        
        Args:
            data: API response dictionary
            
        Returns:
            SentMessage instance
        """
        return cls(
            zaap_id=data.get('zaapId', ''),
            message_id=data.get('messageId', ''),
            id=data.get('id', data.get('messageId', ''))
        )
    
    def __str__(self) -> str:
        return f"SentMessage(message_id={self.message_id})"
