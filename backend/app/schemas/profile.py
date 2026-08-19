from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict

Language = Literal["en", "hi"]
IncomeBand = Literal["under15", "15to3", "3to5", "above5", "unknown"]
LocationType = Literal["rural", "town", "city", "unknown"]
YesNoUnknown = Literal["yes", "no", "unknown"]
Situation = Literal[
    "student", "jobseeker", "employed", "farmer", "selfEmployed", "homemaker", "retired", "other"
]
DocumentId = Literal[
    "identity", "address", "income", "education", "land", "bank", "enrollment", "referral", "businessPlan"
]
EducationStage = Literal["higher", "school", "other", "unknown"]
Landholding = Literal["none", "marginal", "small", "large", "unknown"]


class ProfileIn(BaseModel):
    """Mirrors src/types.ts `Profile` field-for-field. `extra="forbid"` is
    the enforcement mechanism for "no PII fields ever enter this schema":
    any unexpected field (name, phone, aadhaar, bankAccount, address, ...)
    is rejected with a 422 rather than silently accepted or ignored."""

    model_config = ConfigDict(extra="forbid")

    age: Optional[int] = None
    region: Optional[str] = None
    language: Language = "en"
    householdSize: Optional[int] = None
    incomeBand: IncomeBand = "unknown"
    location: LocationType = "unknown"
    cleanCooking: YesNoUnknown = "unknown"
    situations: List[Situation] = []
    educationStage: Optional[EducationStage] = "unknown"
    enrolled: Optional[YesNoUnknown] = "unknown"
    landholding: Optional[Landholding] = "unknown"
    trainingArea: Optional[str] = None
    planningBusiness: Optional[YesNoUnknown] = "unknown"
    documents: List[DocumentId] = []


class ProfileOut(ProfileIn):
    id: str
    createdAt: datetime
    updatedAt: datetime
