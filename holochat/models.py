from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, computed_field

from .settings import load_settings


settings = load_settings()

def time_diff_seconds(start: datetime, end: datetime) -> float:
    return (end - start).total_seconds()

class MessageStaleness(str, Enum):
    NONE = "none"
    FRESH = "fresh"
    STALE = "stale"
    EXPIRED = "expired"
    
class MessageStatus(str, Enum):
    NEW = "new"
    READ = "read"
    
class MessageContent(BaseModel):
    """The raw message that arrives from the client."""
    message: str
    sender: str = 'unknown'

class MessageHold(BaseModel):
    """The message that is held in the server, until a first GET request is made."""
    message: str
    sender: str
    target: str
    recv_time: datetime = Field(default_factory=datetime.now)
    message_freshness: MessageStaleness = MessageStaleness.NONE
    message_status: MessageStatus = MessageStatus.NEW
    
class MessageRequest(BaseModel):
    """The message that is returned to the client, after a GET request is made."""
    message: str
    sender: str
    target: str
    recv_time: datetime
    request_time: datetime = Field(default_factory=datetime.now)
    read_count: int = 0
    
    @computed_field
    @property
    def message_age_secs(self) -> float:
        """Calculated message age in seconds between receive and request."""
        return time_diff_seconds(self.recv_time, self.request_time)
    
    @computed_field
    @property
    def message_freshness(self) -> MessageStaleness:
        """Calculated message freshness based on age in seconds."""
        if self.message_age_secs < settings.message_stale_secs:
            return MessageStaleness.FRESH
        elif self.message_age_secs < settings.message_expire_secs:
            return MessageStaleness.STALE
        else:
            return MessageStaleness.EXPIRED
        
    @computed_field
    @property
    def message_status(self) -> MessageStatus:
        """Returns the message status based on read count ('new' or 'read')."""
        if self.read_count == 0:
            return MessageStatus.NEW
        else:
            return MessageStatus.READ
        
class MessageStore(BaseModel):
    messages: list[MessageContent | MessageHold | MessageRequest] = []
    config: dict[str, Any] = {}
    
    @computed_field
    @property
    def message_count(self) -> int:
        """Returns the total number of messages in the database."""
        return len(self.messages)