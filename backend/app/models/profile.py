import uuid
from datetime import datetime
from typing import List, Optional

from sqlmodel import JSON, Column, Field, SQLModel


class Profile(SQLModel, table=True):
    """Mirrors src/types.ts `Profile`. Deliberately excludes name, phone,
    Aadhaar/government IDs, bank details, and precise address - the same
    exclusions the frontend questionnaire enforces. Do not add such fields
    here; see ProfileIn in schemas/profile.py for the enforcement layer."""

    __tablename__ = "profiles"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    session_id: str = Field(foreign_key="anonymous_sessions.id", unique=True, index=True)

    age: Optional[int] = None
    region: Optional[str] = None
    language: str = "en"
    household_size: Optional[int] = None
    income_band: str = "unknown"
    location: str = "unknown"
    clean_cooking: str = "unknown"
    situations: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    education_stage: Optional[str] = "unknown"
    enrolled: Optional[str] = "unknown"
    landholding: Optional[str] = "unknown"
    training_area: Optional[str] = None
    planning_business: Optional[str] = "unknown"
    documents: List[str] = Field(default_factory=list, sa_column=Column(JSON))

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
