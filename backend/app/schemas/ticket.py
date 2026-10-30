from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


TicketPriority = Literal["low", "medium", "high", "critical"]

TicketStatus = Literal["open", "in_progress", "resolved"]

TicketCategory = Literal[
    "hardware",
    "software",
    "network",
    "access",
    "other",
]


class TicketCreate(BaseModel):
    title: str = Field(min_length=5, max_length=200)
    description: str = Field(min_length=10)
    priority: TicketPriority = "medium"
    category: TicketCategory = "other"


class TicketResponse(BaseModel):
    id: int
    title: str
    description: str
    status: TicketStatus
    priority: TicketPriority
    category: TicketCategory
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TicketStatusUpdate(BaseModel):
    status: TicketStatus