
def test_create_ticket(client):
    response = client.post(
        "/api/v1/tickets",
        json={
            "title": "Erro ao acessar o sistema",
            "description": (
                "O usuário recebe um erro ao tentar "
                "entrar no painel."
            ),
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["title"] == "Erro ao acessar o sistema"
    assert data["status"] == "open"
    assert "created_at" in data


def test_list_tickets(client):
    client.post(
        "/api/v1/tickets",
        json={
            "title": "Falha na conexão",
            "description": (
                "O sistema não consegue conectar "
                "ao servidor."
            ),
        },
    )

    response = client.get("/api/v1/tickets")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Falha na conexão"


def test_get_nonexistent_ticket(client):
    response = client.get("/api/v1/tickets/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Chamado não encontrado"


def test_create_ticket_rejects_short_title(client):
    response = client.post(
        "/api/v1/tickets",
        json={
            "title": "Erro",
            "description": "O sistema apresenta uma falha ao entrar.",
        },
    )

    assert response.status_code == 422


def test_create_ticket_rejects_short_description(client):
    response = client.post(
        "/api/v1/tickets",
        json={
            "title": "Erro ao acessar o sistema",
            "description": "Falha",
        },
    )

    assert response.status_code == 422


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
