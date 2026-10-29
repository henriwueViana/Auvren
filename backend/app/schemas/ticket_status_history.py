from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TicketStatusHistoryResponse(BaseModel):
    id: int
    ticket_id: int
    previous_status: str
    new_status: str
    changed_at: datetime

    model_config = ConfigDict(from_attributes=True)
