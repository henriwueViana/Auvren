
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



def test_inactive_user_cannot_access_protected_route(
    client,
    authenticated_client,
    db_session,
):
    from app.models.user import User

    user = db_session.query(User).filter_by(
        email="teste@auvren.com"
    ).first()

    assert user is not None

    user.is_active = False
    db_session.commit()

    response = authenticated_client.get("/api/v1/tickets")

    assert response.status_code == 401


def test_non_admin_cannot_create_users(
    authenticated_client,
    db_session,
):
    from app.models.user import User

    user = db_session.query(User).filter_by(
        email="teste@auvren.com"
    ).first()

    assert user is not None

    user.role = "agent"
    db_session.commit()

    response = authenticated_client.post(
        "/api/v1/users",
        json={
            "name": "Agente de Teste",
            "email": "agente@example.com",
            "password": "SenhaSegura123",
        },
    )

    assert response.status_code == 403



def test_register_rejects_duplicate_email(authenticated_client):
    response = authenticated_client.post(
        "/api/v1/auth/register",
        json={
            "organization_name": "Outra Organização",
            "name": "Usuário Duplicado",
            "email": "teste@auvren.com",
            "password": "SenhaSegura123",
        },
    )

    assert response.status_code == 409
    assert "detail" in response.json()


def test_login_rejects_invalid_credentials(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "inexistente@auvren.com",
            "password": "SenhaIncorreta123",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "E-mail ou senha inválidos."


def test_token_without_subject_is_rejected(client):
    from app.core.security import create_access_token

    token = create_access_token({"email": "teste@auvren.com"})

    response = client.get(
        "/api/v1/tickets",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Não foi possível validar as credenciais."
    )
