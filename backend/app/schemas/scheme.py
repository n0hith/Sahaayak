from typing import Dict, List, Literal, Optional, Union

from pydantic import BaseModel


class RuleOut(BaseModel):
    field: str
    operator: Literal["ageBetween", "incomeAtMost", "includes", "equals", "oneOf"]
    value: Union[str, int, List[str]]
    label: str


class SchemeOut(BaseModel):
    id: str
    name: str
    icon: str
    category: str
    summary: str
    whoItMayHelp: str
    support: str
    rules: List[RuleOut]
    requiredDocuments: List[str]
    optionalDocuments: Optional[List[str]] = None
    preparationTime: str
    nextSteps: List[str]
    availability: str
    privacyNote: str


class SchemeListResponse(BaseModel):
    schemes: List[SchemeOut]
    documentLabels: Dict[str, str]


class ExplanationResponse(BaseModel):
    explanation: str
