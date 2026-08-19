from typing import List, Literal

from pydantic import BaseModel

from .scheme import SchemeOut

MatchLevel = Literal["strong", "possible", "moreInfo", "explore"]


class MatchResultOut(BaseModel):
    scheme: SchemeOut
    level: MatchLevel
    reasons: List[str]
    missingInfo: List[str]
    missingDocuments: List[str]
    failedRules: List[str]


class MatchResponse(BaseModel):
    matches: List[MatchResultOut]
    simpleTerms: str
