from datetime import datetime
from typing import Literal

from pydantic import BaseModel

Route = Literal["online", "centre", "helper"]


class HandoffRequest(BaseModel):
    schemeId: str
    planId: str
    route: Route


class ReferenceOut(BaseModel):
    referenceCode: str
    route: Route
    schemeId: str
    planId: str
    completedTasks: int
    totalTasks: int
    status: Literal["Preparation complete", "Documents still needed"]
    createdAt: datetime
