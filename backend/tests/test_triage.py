from unittest.mock import patch

from app.core.security import create_access_token
from app.models import Organization, User
from app.services.triage_service import TriageProviderError


VALID_AI_RESPONSE = {
    "category": "access",
    "priority": "high",
    "justification": "O usuário não consegue acessar o sistema.",
}


def create_test_ticket(client):
    response = client.post(
        "/api/v1/tickets",
        json={
            "title": "Erro ao acessar o sistema",
            "description": "O usuário recebe um erro ao tentar entrar no painel.",
        },
    )

    assert response.status_code == 201
    return response.json()


def create_other_organization_user(db):
    organization = Organization(name="Outra Organização")
    db.add(organization)
    db.commit()
    db.refresh(organization)

    user = User(
        name="Outro Usuário",
        email="outro@teste.com",
        hashed_password="senha_hash",
        organization_id=organization.id,
        role="admin",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@patch("app.services.triage_service.analyze_ticket")
def test_create_ticket_triage(mock_analyze, authenticated_client):
    mock_analyze.return_value = VALID_AI_RESPONSE

    ticket = create_test_ticket(authenticated_client)

    response = authenticated_client.post(
        f"/api/v1/tickets/{ticket['id']}/triage"
    )

    assert response.status_code == 201

    data = response.json()

    assert data["ticket_id"] == ticket["id"]
    assert data["suggested_category"] == "access"
    assert data["suggested_priority"] == "high"
    assert data["review_status"] == "pending"
    assert data["justification"] == VALID_AI_RESPONSE["justification"]

    mock_analyze.assert_called_once()


@patch("app.services.triage_service.analyze_ticket")
def test_create_triage_rejects_invalid_category(
    mock_analyze,
    authenticated_client,
):
    mock_analyze.return_value = {
        **VALID_AI_RESPONSE,
        "category": "finance",
    }

    ticket = create_test_ticket(authenticated_client)

    response = authenticated_client.post(
        f"/api/v1/tickets/{ticket['id']}/triage"
    )

    assert response.status_code == 502
    assert response.json()["detail"] == "A IA retornou uma categoria inválida."


@patch("app.services.triage_service.analyze_ticket")
def test_create_triage_rejects_invalid_priority(
    mock_analyze,
    authenticated_client,
):
    mock_analyze.return_value = {
        **VALID_AI_RESPONSE,
        "priority": "urgent",
    }

    ticket = create_test_ticket(authenticated_client)

    response = authenticated_client.post(
        f"/api/v1/tickets/{ticket['id']}/triage"
    )

    assert response.status_code == 502
    assert response.json()["detail"] == "A IA retornou uma prioridade inválida."


@patch("app.services.triage_service.analyze_ticket")
def test_create_triage_handles_provider_error(
    mock_analyze,
    authenticated_client,
):
    mock_analyze.side_effect = TriageProviderError(
        "O serviço de IA está temporariamente indisponível."
    )

    ticket = create_test_ticket(authenticated_client)

    response = authenticated_client.post(
        f"/api/v1/tickets/{ticket['id']}/triage"
    )

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "O serviço de IA está temporariamente indisponível."
    )


@patch("app.services.triage_service.analyze_ticket")
def test_list_ticket_triages(
    mock_analyze,
    authenticated_client,
):
    mock_analyze.return_value = VALID_AI_RESPONSE

    ticket = create_test_ticket(authenticated_client)

    authenticated_client.post(
        f"/api/v1/tickets/{ticket['id']}/triage"
    )

    response = authenticated_client.get(
        f"/api/v1/tickets/{ticket['id']}/triages"
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["review_status"] == "pending"


@patch("app.services.triage_service.analyze_ticket")
def test_accept_triage_updates_ticket(
    mock_analyze,
    authenticated_client,
):
    mock_analyze.return_value = VALID_AI_RESPONSE

    ticket = create_test_ticket(authenticated_client)

    triage_response = authenticated_client.post(
        f"/api/v1/tickets/{ticket['id']}/triage"
    )

    triage_id = triage_response.json()["id"]

    response = authenticated_client.patch(
        f"/api/v1/tickets/{ticket['id']}/triages/{triage_id}/review",
        json={"review_status": "accepted"},
    )

    assert response.status_code == 200
    assert response.json()["review_status"] == "accepted"

    updated_ticket = authenticated_client.get(
        f"/api/v1/tickets/{ticket['id']}"
    ).json()

    assert updated_ticket["category"] == "access"
    assert updated_ticket["priority"] == "high"


@patch("app.services.triage_service.analyze_ticket")
def test_reject_triage_preserves_ticket_data(
    mock_analyze,
    authenticated_client,
):
    mock_analyze.return_value = VALID_AI_RESPONSE

    ticket = create_test_ticket(authenticated_client)

    triage_response = authenticated_client.post(
        f"/api/v1/tickets/{ticket['id']}/triage"
    )

    triage_id = triage_response.json()["id"]

    response = authenticated_client.patch(
        f"/api/v1/tickets/{ticket['id']}/triages/{triage_id}/review",
        json={"review_status": "rejected"},
    )

    assert response.status_code == 200
    assert response.json()["review_status"] == "rejected"

    updated_ticket = authenticated_client.get(
        f"/api/v1/tickets/{ticket['id']}"
    ).json()

    assert updated_ticket["category"] == ticket["category"]
    assert updated_ticket["priority"] == ticket["priority"]


@patch("app.services.triage_service.analyze_ticket")
def test_triage_cannot_be_reviewed_twice(
    mock_analyze,
    authenticated_client,
):
    mock_analyze.return_value = VALID_AI_RESPONSE

    ticket = create_test_ticket(authenticated_client)

    triage_response = authenticated_client.post(
        f"/api/v1/tickets/{ticket['id']}/triage"
    )

    triage_id = triage_response.json()["id"]

    first_review = authenticated_client.patch(
        f"/api/v1/tickets/{ticket['id']}/triages/{triage_id}/review",
        json={"review_status": "accepted"},
    )

    second_review = authenticated_client.patch(
        f"/api/v1/tickets/{ticket['id']}/triages/{triage_id}/review",
        json={"review_status": "rejected"},
    )

    assert first_review.status_code == 200
    assert second_review.status_code == 409


def test_other_organization_cannot_access_ticket_triages(
    authenticated_client,
    db_session,
):
    ticket = create_test_ticket(authenticated_client)
    other_user = create_other_organization_user(db_session)

    token = create_access_token(
        data={"sub": str(other_user.id)}
    )

    authenticated_client.headers.update({
        "Authorization": f"Bearer {token}"
    })

    response = authenticated_client.get(
        f"/api/v1/tickets/{ticket['id']}/triages"
    )

    assert response.status_code == 404


def test_other_organization_cannot_create_triage(
    authenticated_client,
    db_session,
):
    ticket = create_test_ticket(authenticated_client)
    other_user = create_other_organization_user(db_session)

    token = create_access_token(
        data={"sub": str(other_user.id)}
    )

    authenticated_client.headers.update({
        "Authorization": f"Bearer {token}"
    })

    response = authenticated_client.post(
        f"/api/v1/tickets/{ticket['id']}/triage"
    )

    assert response.status_code == 404