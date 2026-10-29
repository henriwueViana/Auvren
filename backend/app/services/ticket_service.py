
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ticket import Ticket
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

    ticket.status = new_status
    db.commit()
    db.refresh(ticket)

    return ticket

def test_update_ticket_status(client):
    create_response = client.post(
        "/api/v1/tickets",
        json={
            "title": "Erro ao acessar o sistema",
            "description": "O usuário não consegue entrar no painel.",
        },
    )

    ticket_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/tickets/{ticket_id}/status",
        json={"status": "in_progress"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"


def test_update_nonexistent_ticket_status(client):
    response = client.patch(
        "/api/v1/tickets/999/status",
        json={"status": "resolved"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Chamado não encontrado"


def test_update_ticket_with_invalid_status(client):
    create_response = client.post(
        "/api/v1/tickets",
        json={
            "title": "Erro ao acessar o sistema",
            "description": "O usuário não consegue entrar no painel.",
        },
    )

    ticket_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/tickets/{ticket_id}/status",
        json={"status": "closed"},
    )

    assert response.status_code == 422
