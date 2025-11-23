"""Group-related types and classes."""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Literal


@dataclass
class GroupCreated:
    """
    Group creation response.
    
    Attributes:
        group_id: Created group ID
        invite_link: Group invite link (if applicable)
    """
    group_id: str
    invite_link: str | None = None
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GroupCreated:
        """Create from API response."""
        return cls(
            group_id=data.get('groupId', data.get('id', '')),
            invite_link=data.get('inviteLink')
        )


@dataclass
class GroupParticipant:
    """Group participant information."""
    phone: str
    is_admin: bool = False
    is_super_admin: bool = False
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GroupParticipant:
        """Create from API response."""
        return cls(
            phone=data.get('phone', data.get('id', '')),
            is_admin=data.get('isAdmin', False),
            is_super_admin=data.get('isSuperAdmin', False)
        )


@dataclass
class GroupMetadata:
    """
    Complete group metadata.
    
    Attributes:
        group_id: Group ID
        owner: Group owner phone
        subject: Group name/subject
        subject_time: When subject was last changed
        subject_owner: Who changed the subject
        creation: Group creation timestamp
        participants: List of participants
        size: Number of participants
        description: Group description
        description_owner: Who set the description
        description_id: Description ID
        restrict: Restrict who can send messages
        announce: Announce mode (only admins can send)
        no_frequent_call: Disable frequent calls
        ephemeral: Ephemeral messages duration
    """
    group_id: str
    owner: str
    subject: str
    subject_time: int
    subject_owner: str
    creation: int
    participants: list[GroupParticipant]
    size: int
    description: str | None = None
    description_owner: str | None = None
    description_id: str | None = None
    restrict: bool = False
    announce: bool = False
    no_frequent_call: bool = False
    ephemeral: int | None = None
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GroupMetadata:
        """Create from API response."""
        participants = [
            GroupParticipant.from_dict(p)
            for p in data.get('participants', [])
        ]
        
        return cls(
            group_id=data.get('id', ''),
            owner=data.get('owner', ''),
            subject=data.get('subject', ''),
            subject_time=data.get('subjectTime', 0),
            subject_owner=data.get('subjectOwner', ''),
            creation=data.get('creation', 0),
            participants=participants,
            size=data.get('size', len(participants)),
            description=data.get('desc'),
            description_owner=data.get('descOwner'),
            description_id=data.get('descId'),
            restrict=data.get('restrict', False),
            announce=data.get('announce', False),
            no_frequent_call=data.get('noFrequentlyForwarded', False),
            ephemeral=data.get('ephemeralDuration'),
        )


@dataclass
class GroupInviteInfo:
    """
    Group invitation information.
    
    Attributes:
        invite_code: Invitation code
        invite_link: Full invitation link
        expiration: Expiration timestamp (if applicable)
    """
    invite_code: str
    invite_link: str
    expiration: int | None = None
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GroupInviteInfo:
        """Create from API response."""
        return cls(
            invite_code=data.get('inviteCode', data.get('code', '')),
            invite_link=data.get('inviteLink', data.get('link', '')),
            expiration=data.get('expiration')
        )
