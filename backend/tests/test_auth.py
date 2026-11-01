
def register_and_get_token(client, organization, name, email):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "organization_name": organization,
            "name": name,
            "email": email,
            "password": "SenhaSegura123",
        },
    )

    assert response.status_code == 201, response.text

    return response.json()["access_token"]


def test_tickets_require_authentication(client):
    requests = [
        ("GET", "/api/v1/tickets", None),
        ("POST", "/api/v1/tickets", {
            "title": "Chamado de teste",
            "description": "Descrição do chamado de teste",
        }),
        ("GET", "/api/v1/tickets/1", None),
        ("PATCH", "/api/v1/tickets/1/status", {
            "status": "in_progress",
        }),
        ("GET", "/api/v1/tickets/1/history", None),
    ]

    for method, url, payload in requests:
        response = client.request(
            method,
            url,
            json=payload,
        )

        assert response.status_code == 401, (
            f"{method} {url}: esperado 401, recebido "
            f"{response.status_code}"
        )


def test_tickets_reject_invalid_token(client):
    client.headers.update({
        "Authorization": "Bearer token_invalido"
    })

    response = client.get("/api/v1/tickets")

    assert response.status_code == 401


def test_organizations_cannot_access_each_others_tickets(client):
    token_a = register_and_get_token(
        client,
        "Organização A",
        "Usuário A",
        "usuario.a@example.com",
    )

    token_b = register_and_get_token(
        client,
        "Organização B",
        "Usuário B",
        "usuario.b@example.com",
    )

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}

    ticket_response = client.post(
        "/api/v1/tickets",
        headers=headers_a,
        json={
            "title": "Chamado privado da organização A",
            "description": "Este chamado pertence somente à organização A.",
        },
    )

    assert ticket_response.status_code == 201, ticket_response.text

    ticket_id = ticket_response.json()["id"]

    # Organização B não deve visualizar o chamado na listagem.
    list_response = client.get(
        "/api/v1/tickets",
        headers=headers_b,
    )

    assert list_response.status_code == 200
    assert all(
        ticket["id"] != ticket_id
        for ticket in list_response.json()
    )

    # Organização B não deve consultar o chamado.
    get_response = client.get(
        f"/api/v1/tickets/{ticket_id}",
        headers=headers_b,
    )

    assert get_response.status_code == 404

    # Organização B não deve alterar seu status.
    update_response = client.patch(
        f"/api/v1/tickets/{ticket_id}/status",
        headers=headers_b,
        json={"status": "in_progress"},
    )

    assert update_response.status_code == 404

    # Organização B não deve consultar seu histórico.
    history_response = client.get(
        f"/api/v1/tickets/{ticket_id}/history",
        headers=headers_b,
    )

    assert history_response.status_code == 404

    # A organização A continua tendo acesso ao próprio chamado.
    owner_response = client.get(
        f"/api/v1/tickets/{ticket_id}",
        headers=headers_a,
    )

    assert owner_response.status_code == 200

def test_inactive_user_cannot_access_protected_route(client, authenticated_client):
    from app.core.database import get_db
    from app.models import User

    db = next(app.dependency_overrides[get_db]())
    user = db.query(User).filter_by(email="teste@auvren.com").first()
    user.is_active = False
    db.commit()
    db.close()

    response = authenticated_client.get("/api/v1/tickets")

    assert response.status_code == 401


def test_non_admin_cannot_access_admin_route(authenticated_client):
    response = authenticated_client.get("/api/v1/users")

    assert response.status_code == 403
