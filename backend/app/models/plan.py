import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Plan(SQLModel, table=True):
    """A saved preparation plan for one scheme, owned by one anonymous
    session. Unlike the frontend's single-plan localStorage model, a
    session may hold many plans (one per scheme it has started), which is
    what lets `/api/plans` return a real list."""

    __tablename__ = "plans"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    session_id: str = Field(foreign_key="anonymous_sessions.id", index=True)
    scheme_id: str = Field(foreign_key="schemes.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PlanTask(SQLModel, table=True):
    """One checklist item within a Plan. `task_key` is the stable id used
    by the frontend (e.g. "doc-identity", "official-instructions") -
    distinct from the surrogate `id` primary key."""

    __tablename__ = "plan_tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    plan_id: str = Field(foreign_key="plans.id", index=True)
    task_key: str
    title: str
    description: str
    status: str  # available | needed | optional
    done: bool = False
