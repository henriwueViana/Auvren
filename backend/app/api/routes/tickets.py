
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.ticket import TicketCreate, TicketResponse
from app.services.ticket_service import (
    create_ticket,
    get_ticket,
    list_tickets,
)

router = APIRouter(prefix="/api/v1/tickets", tags=["Tickets"])


@router.post(
    "",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_ticket_endpoint(
    data: TicketCreate,
    db: Session = Depends(get_db),
):
    return create_ticket(db, data)


@router.get("", response_model=list[TicketResponse])
def list_tickets_endpoint(db: Session = Depends(get_db)):
    return list_tickets(db)


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket_endpoint(
    ticket_id: int,
    db: Session = Depends(get_db),
):
    ticket = get_ticket(db, ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chamado não encontrado",
        )

    return ticket
