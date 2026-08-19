import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class ReferenceRequest(SQLModel, table=True):
    """A synthetic 'readiness reference', created by the mock hand-off
    flow. This never represents a submitted application - see
    reference_generator.py and routers/handoff.py."""

    __tablename__ = "reference_requests"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    session_id: str = Field(foreign_key="anonymous_sessions.id", index=True)
    scheme_id: str = Field(foreign_key="schemes.id", index=True)
    plan_id: str = Field(foreign_key="plans.id", index=True)
    route: str  # online | centre | helper
    reference_code: str = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
