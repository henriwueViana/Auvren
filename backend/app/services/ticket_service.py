
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ticket import Ticket
from app.models.ticket_status_history import TicketStatusHistory
from app.schemas.ticket import TicketCreate


def create_ticket(db: Session, data: TicketCreate) -> Ticket:
    ticket = Ticket(
        title=data.title,
        description=data.description,
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return ticket


def list_tickets(db: Session) -> list[Ticket]:
    statement = select(Ticket).order_by(Ticket.created_at.desc())
    return list(db.scalars(statement).all())


def get_ticket(db: Session, ticket_id: int) -> Ticket | None:
    return db.get(Ticket, ticket_id)


def update_ticket_status(
    db: Session,
    ticket_id: int,
    new_status: str,
) -> Ticket | None:
    ticket = db.get(Ticket, ticket_id)

    if ticket is None:
        return None

    # Não registra histórico se o status não mudou.
    if ticket.status == new_status:
        return ticket

    history_entry = TicketStatusHistory(
        ticket_id=ticket.id,
        previous_status=ticket.status,
        new_status=new_status,
    )

    ticket.status = new_status
    db.add(history_entry)

    # Salva a alteração e o histórico na mesma transação.
    db.commit()
    db.refresh(ticket)

    return ticket


def list_ticket_status_history(
    db: Session,
    ticket_id: int,
) -> list[TicketStatusHistory] | None:
    ticket = db.get(Ticket, ticket_id)

    if ticket is None:
        return None

    statement = (
        select(TicketStatusHistory)
        .where(TicketStatusHistory.ticket_id == ticket_id)
        .order_by(
            TicketStatusHistory.changed_at.asc(),
            TicketStatusHistory.id.asc(),
        )
    )

    return list(db.scalars(statement).all())
