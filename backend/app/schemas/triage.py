
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


TriageCategory = Literal[
    "hardware",
    "software",
    "network",
    "access",
    "other",
]

TriagePriority = Literal[
    "low",
    "medium",
    "high",
    "critical",
]

TriageReviewStatus = Literal[
    "pending",
    "accepted",
    "rejected",
]


class TicketTriageResponse(BaseModel):
    id: int
    ticket_id: int
    suggested_category: TriageCategory
    suggested_priority: TriagePriority
    justification: str
    model: str
    review_status: TriageReviewStatus
    reviewed_by: int | None
    created_at: datetime
    reviewed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class TicketTriageReview(BaseModel):
    review_status: Literal["accepted", "rejected"]

    model_config = ConfigDict(extra="forbid")
