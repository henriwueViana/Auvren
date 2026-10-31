
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.ticket import Ticket
from app.models.ticket_status_history import TicketStatusHistory
from app.schemas.ticket import TicketCreate


ALLOWED_STATUS_TRANSITIONS = {
    "open": {"in_progress"},
    "in_progress": {"resolved"},
    "resolved": {"in_progress"},
}


class InvalidStatusTransition(Exception):
    pass


def create_ticket(
    db: Session,
    data: TicketCreate,
    organization_id: int,
) -> Ticket:
    ticket = Ticket(
        organization_id=organization_id,
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
    organization_id: int,
    page: int = 1,
    limit: int = 10,
    status: str | None = None,
    priority: str | None = None,
    category: str | None = None,
    search: str | None = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> list[Ticket]:
    statement = select(Ticket).where(
        Ticket.organization_id == organization_id
    )

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

    if priority:
        statement = statement.where(Ticket.priority == priority)

    if category:
        statement = statement.where(Ticket.category == category)

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


def get_ticket(
    db: Session,
    ticket_id: int,
    organization_id: int,
) -> Ticket | None:
    statement = select(Ticket).where(
        Ticket.id == ticket_id,
        Ticket.organization_id == organization_id,
    )

    return db.scalar(statement)


def update_ticket_status(
    db: Session,
    ticket_id: int,
    new_status: str,
    organization_id: int,
) -> Ticket | None:
    ticket = get_ticket(db, ticket_id, organization_id)

    if ticket is None:
        return None

    # Não registra histórico se o status não mudou.
    if ticket.status == new_status:
        return ticket

    if new_status not in ALLOWED_STATUS_TRANSITIONS.get(
        ticket.status, set()
    ):
        raise InvalidStatusTransition(
            f"Não é permitido alterar de '{ticket.status}' para '{new_status}'."
        )

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
    organization_id: int,
) -> list[TicketStatusHistory] | None:
    ticket = get_ticket(db, ticket_id, organization_id)

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
