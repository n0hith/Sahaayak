from typing import List, Optional, Union

from sqlmodel import JSON, Column, Field, SQLModel


class Scheme(SQLModel, table=True):
    """Mirrors src/types.ts `Scheme`. Seeded from app/seed/schemes_seed.py,
    a direct transcription of src/data/schemes.ts. Every scheme here is
    fictional demo data - see `privacy_note` and the "(example)" document
    labels in app/seed/document_labels.py."""

    __tablename__ = "schemes"

    id: str = Field(primary_key=True)
    name: str
    icon: str
    category: str
    summary: str
    who_it_may_help: str
    support: str
    required_documents: List[str] = Field(sa_column=Column(JSON))
    optional_documents: Optional[List[str]] = Field(default=None, sa_column=Column(JSON))
    preparation_time: str
    next_steps: List[str] = Field(sa_column=Column(JSON))
    availability: str
    privacy_note: str


class Rule(SQLModel, table=True):
    """Mirrors src/types.ts `Rule`. `value` can be a string, an int-like
    range string ("17-25"), or a list of strings, exactly as in schemes.ts,
    so it is stored as JSON rather than a typed column."""

    __tablename__ = "rules"

    id: Optional[int] = Field(default=None, primary_key=True)
    scheme_id: str = Field(foreign_key="schemes.id", index=True)
    field: str
    operator: str
    value: Union[str, int, List[str]] = Field(sa_column=Column(JSON))
    label: str
