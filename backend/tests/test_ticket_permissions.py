
import pytest

from app.core.security import create_access_token
from app.models.user import User
from app.models.organization import Organization


def auth_headers(user):
    token = create_access_token({"sub": str(user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def permission_users(db_session):
    org_a = Organization(name="Empresa Segurança A")
    org_b = Organization(name="Empresa Segurança B")

    db_session.add_all([org_a, org_b])
    db_session.flush()

    users = {}

    for key, name, role, org in [
        ("admin", "Administrador", "admin", org_a),
        ("agent", "Agente", "agent", org_a),
        ("alice", "Alice", "requester", org_a),
        ("bob", "Bob", "requester", org_a),
        ("external", "Externo", "requester", org_b),
    ]:
        user = User(
            name=name,
            email=f"{key}@permissions.example.com",
            hashed_password="senha_de_teste_nao_utilizada",
            role=role,
            organization_id=org.id,
            is_active=True,
        )
        db_session.add(user)
        users[key] = user

    db_session.commit()

    for user in users.values():
        db_session.refresh(user)

    return users


def create_ticket(client, user, title):
    response = client.post(
        "/api/v1/tickets",
        headers=auth_headers(user),
        json={
            "title": title,
            "description": "Descrição para testar isolamento e permissões.",
            "priority": "medium",
            "category": "software",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_requester_can_access_own_ticket(client, permission_users):
    alice = permission_users["alice"]
    ticket_id = create_ticket(client, alice, "Chamado da Alice")

    response = client.get(
        f"/api/v1/tickets/{ticket_id}",
        headers=auth_headers(alice),
    )

    assert response.status_code == 200
    assert response.json()["id"] == ticket_id


def test_requester_cannot_access_other_ticket(client, permission_users):
    alice = permission_users["alice"]
    bob = permission_users["bob"]

    ticket_id = create_ticket(client, alice, "Chamado privado da Alice")

    response = client.get(
        f"/api/v1/tickets/{ticket_id}",
        headers=auth_headers(bob),
    )

    assert response.status_code == 404


def test_requester_list_contains_only_own_tickets(client, permission_users):
    alice = permission_users["alice"]
    bob = permission_users["bob"]

    alice_ticket = create_ticket(client, alice, "Chamado exclusivo da Alice")
    bob_ticket = create_ticket(client, bob, "Chamado exclusivo do Bob")

    response = client.get(
        "/api/v1/tickets",
        headers=auth_headers(alice),
    )

    assert response.status_code == 200

    ticket_ids = {ticket["id"] for ticket in response.json()}

    assert alice_ticket in ticket_ids
    assert bob_ticket not in ticket_ids


def test_requester_cannot_access_other_ticket_history(client, permission_users):
    alice = permission_users["alice"]
    bob = permission_users["bob"]

    ticket_id = create_ticket(client, alice, "Chamado com histórico privado")

    response = client.get(
        f"/api/v1/tickets/{ticket_id}/history",
        headers=auth_headers(bob),
    )

    assert response.status_code == 404


def test_requester_cannot_access_other_organization(client, permission_users):
    alice = permission_users["alice"]
    external = permission_users["external"]

    ticket_id = create_ticket(client, external, "Chamado de outra organização")

    response = client.get(
        f"/api/v1/tickets/{ticket_id}",
        headers=auth_headers(alice),
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    "method,path,payload",
    [
        ("PATCH", "/status", {"status": "in_progress"}),
        ("POST", "/triage", None),
        ("GET", "/triages", None),
        ("PATCH", "/triages/1/review", {"review_status": "approved"}),
    ],
)
def test_requester_cannot_manage_ticket(
    client,
    permission_users,
    method,
    path,
    payload,
):
    alice = permission_users["alice"]
    ticket_id = create_ticket(client, alice, "Chamado sem acesso administrativo")

    response = client.request(
        method,
        f"/api/v1/tickets/{ticket_id}{path}",
        headers=auth_headers(alice),
        json=payload,
    )

    assert response.status_code == 403, response.text


@pytest.mark.parametrize("role", ["admin", "agent"])
def test_support_can_access_organization_tickets(
    client,
    permission_users,
    role,
):
    alice = permission_users["alice"]
    support_user = permission_users[role]

    ticket_id = create_ticket(client, alice, "Chamado visível ao suporte")

    response = client.get(
        f"/api/v1/tickets/{ticket_id}",
        headers=auth_headers(support_user),
    )

    assert response.status_code == 200
