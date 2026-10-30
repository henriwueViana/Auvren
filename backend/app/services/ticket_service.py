from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.ticket import Ticket
from app.models.ticket_status_history import TicketStatusHistory
from app.schemas.ticket import TicketCreate


def create_ticket(db: Session, data: TicketCreate) -> Ticket:
    ticket = Ticket(
        title=data.title,
        description=data.description,
        priority=data.priority,
        category=data.category,
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return ticket

def list_tickets(
    db: Session,
    page: int = 1,
    limit: int = 10,
    status: str | None = None,
    search: str | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> list[Ticket]:
    statement = select(Ticket)

    if status:
        statement = statement.where(Ticket.status == status)

    if search:
        term = f"%{search.strip()}%"
        statement = statement.where(
            or_(
                Ticket.title.ilike(term),
                Ticket.description.ilike(term),
            )
        )

    sort_columns = {
        "created_at": Ticket.created_at,
        "title": Ticket.title,
        "status": Ticket.status,
        "id": Ticket.id,
    }

    column = sort_columns[sort_by]

    if sort_order == "asc":
        statement = statement.order_by(column.asc())
    else:
        statement = statement.order_by(column.desc())

    statement = statement.offset((page - 1) * limit).limit(limit)

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