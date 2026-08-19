from datetime import datetime
from typing import List, Literal

from pydantic import BaseModel


class PlanTaskOut(BaseModel):
    id: str
    title: str
    description: str
    status: Literal["available", "needed", "optional"]
    done: bool


class PlanOut(BaseModel):
    id: str
    schemeId: str
    tasks: List[PlanTaskOut]
    createdAt: datetime
    updatedAt: datetime


class ExplainTaskRequest(BaseModel):
    taskId: str
    question: Literal["why", "missing", "first"]
