import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class AnonymousSession(SQLModel, table=True):
    """An anonymous, opaque session. Holds no identity data - just a UUID
    and a timestamp. This is the only 'account' concept Sahaayak has."""

    __tablename__ = "anonymous_sessions"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
