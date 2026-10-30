from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.ticket import TicketCreate, TicketResponse, TicketStatusUpdate
from app.schemas.ticket_status_history import TicketStatusHistoryResponse
from app.services.ticket_service import (
    InvalidStatusTransition,
    create_ticket,
    get_ticket,
    list_ticket_status_history,
    list_tickets,
    update_ticket_status,
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
def list_tickets_endpoint(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    status_filter: Literal["open", "in_progress", "resolved"] | None = Query(
        default=None,
        alias="status",
    ),

    priority_filter: Literal["low", "medium", "high", "critical"] | None = Query(
        default=None,
        alias="priority",
    ),
    category_filter: Literal[
        "hardware",
        "software",
        "network",
        "access",
        "other",
    ] | None = Query(
        default=None,
        alias="category",
    ),
    search: str | None = Query(default=None, min_length=1, max_length=200),
    sort_by: Literal["created_at", "title", "status", "id"] = "created_at",
    sort_order: Literal["asc", "desc"] = "desc",
    db: Session = Depends(get_db),
):
    return list_tickets(
        db,
        page=page,
        limit=limit,
        status=status_filter,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        priority=priority_filter,
        category=category_filter,
    )


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


@router.patch("/{ticket_id}/status", response_model=TicketResponse)
def update_ticket_status_endpoint(
    ticket_id: int,
    data: TicketStatusUpdate,
    db: Session = Depends(get_db),
):
    try:
        ticket = update_ticket_status(db, ticket_id, data.status)
    except InvalidStatusTransition as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chamado não encontrado",
        )

    return ticket


@router.get(
    "/{ticket_id}/history",
    response_model=list[TicketStatusHistoryResponse],
)
def list_ticket_status_history_endpoint(
    ticket_id: int,
    db: Session = Depends(get_db),
):
    history = list_ticket_status_history(db, ticket_id)

    if history is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chamado não encontrado",
        )

    return history