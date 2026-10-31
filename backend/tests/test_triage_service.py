
import pytest

from app.models.ticket import Ticket
from app.models.ticket_triage import TicketTriage
from app.services import triage_service
from app.services.triage_service import (
    TriageProviderError,
    create_ticket_triage,
    list_ticket_triages,
    review_ticket_triage,
)


VALID_AI_RESPONSE = {
    "category": "access",
    "priority": "high",
    "justification": "O usuário não consegue acessar o sistema.",
}


def create_ticket_for_service(client, db_session):
    response = client.post(
        "/api/v1/tickets",
        json={
            "title": "Erro ao acessar o sistema",
            "description": "O usuário recebe um erro ao tentar entrar no painel.",
        },
    )

    assert response.status_code == 201

    return db_session.get(Ticket, response.json()["id"])


def test_create_triage_wraps_provider_exception(
    authenticated_client,
    db_session,
    monkeypatch,
):
    ticket = create_ticket_for_service(authenticated_client, db_session)

    def raise_provider_error(**kwargs):
        raise RuntimeError("Falha no provedor")

    monkeypatch.setattr(
        triage_service,
        "analyze_ticket",
        raise_provider_error,
    )

    with pytest.raises(TriageProviderError):
        create_ticket_triage(db_session, ticket)


@pytest.mark.parametrize(
    "ai_response",
    [
        None,
        [],
        "resposta inválida",
    ],
)
def test_create_triage_rejects_non_dict_response(
    authenticated_client,
    db_session,
    monkeypatch,
    ai_response,
):
    ticket = create_ticket_for_service(authenticated_client, db_session)

    monkeypatch.setattr(
        triage_service,
        "analyze_ticket",
        lambda **kwargs: ai_response,
    )

    with pytest.raises(ValueError, match="resposta inválida"):
        create_ticket_triage(db_session, ticket)


@pytest.mark.parametrize(
    "ai_response",
    [
        {**VALID_AI_RESPONSE, "category": None},
        {**VALID_AI_RESPONSE, "category": 123},
        {**VALID_AI_RESPONSE, "category": "finance"},
        {**VALID_AI_RESPONSE, "priority": None},
        {**VALID_AI_RESPONSE, "priority": 123},
        {**VALID_AI_RESPONSE, "priority": "urgent"},
        {**VALID_AI_RESPONSE, "justification": None},
        {**VALID_AI_RESPONSE, "justification": 123},
        {**VALID_AI_RESPONSE, "justification": "   "},
    ],
)
def test_create_triage_rejects_invalid_ai_fields(
    authenticated_client,
    db_session,
    monkeypatch,
    ai_response,
):
    ticket = create_ticket_for_service(authenticated_client, db_session)

    monkeypatch.setattr(
        triage_service,
        "analyze_ticket",
        lambda **kwargs: ai_response,
    )

    with pytest.raises(ValueError):
        create_ticket_triage(db_session, ticket)


def test_create_triage_rolls_back_on_database_error(
    authenticated_client,
    db_session,
    monkeypatch,
):
    ticket = create_ticket_for_service(authenticated_client, db_session)

    monkeypatch.setattr(
        triage_service,
        "analyze_ticket",
        lambda **kwargs: VALID_AI_RESPONSE,
    )

    def raise_database_error():
        raise RuntimeError("Falha no banco")

    monkeypatch.setattr(db_session, "commit", raise_database_error)

    with pytest.raises(RuntimeError, match="Falha no banco"):
        create_ticket_triage(db_session, ticket)

    assert db_session.query(TicketTriage).count() == 0


def test_list_triages_returns_none_for_missing_ticket(db_session):
    result = list_ticket_triages(
        db_session,
        ticket_id=99999,
        organization_id=1,
    )

    assert result is None


def test_review_rejects_invalid_status(
    authenticated_client,
    db_session,
):
    ticket = create_ticket_for_service(authenticated_client, db_session)

    with pytest.raises(ValueError, match="Status de revisão inválido"):
        review_ticket_triage(
            db_session,
            ticket.id,
            1,
            ticket.organization_id,
            1,
            "pending",
        )


def test_review_returns_none_for_missing_ticket(db_session):
    result = review_ticket_triage(
        db_session,
        ticket_id=99999,
        triage_id=1,
        organization_id=1,
        reviewer_id=1,
        review_status="accepted",
    )

    assert result is None


def test_review_returns_none_for_missing_triage(
    authenticated_client,
    db_session,
):
    ticket = create_ticket_for_service(authenticated_client, db_session)

    result = review_ticket_triage(
        db_session,
        ticket_id=ticket.id,
        triage_id=99999,
        organization_id=ticket.organization_id,
        reviewer_id=1,
        review_status="accepted",
    )

    assert result is None


def test_review_rolls_back_on_database_error(
    authenticated_client,
    db_session,
    monkeypatch,
):
    ticket = create_ticket_for_service(authenticated_client, db_session)

    monkeypatch.setattr(
        triage_service,
        "analyze_ticket",
        lambda **kwargs: VALID_AI_RESPONSE,
    )

    triage = create_ticket_triage(db_session, ticket)

    def raise_database_error():
        raise RuntimeError("Falha ao revisar")

    monkeypatch.setattr(db_session, "commit", raise_database_error)

    with pytest.raises(RuntimeError, match="Falha ao revisar"):
        review_ticket_triage(
            db_session,
            ticket.id,
            triage.id,
            ticket.organization_id,
            1,
            "accepted",
        )

    db_session.refresh(triage)
    assert triage.review_status == "pending"
