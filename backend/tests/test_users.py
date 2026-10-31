def register_user(
    client,
    organization,
    name,
    email,
):
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


def test_admin_can_create_agent(authenticated_client):
    response = authenticated_client.post(
        "/api/v1/users",
        json={
            "name": "Agente de Teste",
            "email": "agente@example.com",
            "password": "SenhaSegura123",
        },
    )

    assert response.status_code == 201
    assert response.json()["role"] == "agent"
    assert response.json()["is_active"] is True


def test_admin_can_list_organization_users(authenticated_client):
    response = authenticated_client.get("/api/v1/users")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["role"] == "admin"


def test_agent_cannot_manage_users(client):
    admin_token = register_user(
        client,
        "Organização A",
        "Administrador",
        "admin@example.com",
    )

    client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Agente",
            "email": "agente2@example.com",
            "password": "SenhaSegura123",
        },
    )

    agent_token = client.post(
        "/api/v1/auth/login",
        json={
            "email": "agente2@example.com",
            "password": "SenhaSegura123",
        },
    ).json()["access_token"]

    headers = {"Authorization": f"Bearer {agent_token}"}

    create_response = client.post(
        "/api/v1/users",
        headers=headers,
        json={
            "name": "Outro Agente",
            "email": "outro@example.com",
            "password": "SenhaSegura123",
        },
    )

    list_response = client.get(
        "/api/v1/users",
        headers=headers,
    )

    assert create_response.status_code == 403
    assert list_response.status_code == 403


def test_admin_only_sees_own_organization_users(client):
    token_a = register_user(
        client,
        "Organização A",
        "Admin A",
        "admin.a@example.com",
    )

    token_b = register_user(
        client,
        "Organização B",
        "Admin B",
        "admin.b@example.com",
    )

    client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token_a}"},
        json={
            "name": "Agente A",
            "email": "agente.a@example.com",
            "password": "SenhaSegura123",
        },
    )

    response_a = client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token_a}"},
    )

    response_b = client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token_b}"},
    )

    assert response_a.status_code == 200
    assert response_b.status_code == 200

    assert len(response_a.json()) == 2
    assert len(response_b.json()) == 1

    assert all(
        user["organization_id"] == response_a.json()[0]["organization_id"]
        for user in response_a.json()
    )


def test_user_creation_rejects_invalid_data(authenticated_client):
    response = authenticated_client.post(
        "/api/v1/users",
        json={
            "name": "A",
            "email": "email-invalido",
            "password": "123",
        },
    )

    assert response.status_code == 422


def test_user_creation_rejects_duplicate_email(authenticated_client):
    authenticated_client.post(
        "/api/v1/users",
        json={
            "name": "Agente",
            "email": "duplicado@example.com",
            "password": "SenhaSegura123",
        },
    )

    response = authenticated_client.post(
        "/api/v1/users",
        json={
            "name": "Outro Agente",
            "email": "duplicado@example.com",
            "password": "SenhaSegura123",
        },
    )

    assert response.status_code == 409
