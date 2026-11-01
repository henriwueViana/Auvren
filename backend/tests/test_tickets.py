
def test_create_ticket(authenticated_client):
    response = authenticated_client.post(
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


def test_list_tickets(authenticated_client):
    authenticated_client.post(
        "/api/v1/tickets",
        json={
            "title": "Falha na conexão",
            "description": (
                "O sistema não consegue conectar "
                "ao servidor."
            ),
        },
    )

    response = authenticated_client.get("/api/v1/tickets")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Falha na conexão"


def test_get_nonexistent_ticket(authenticated_client):
    response = authenticated_client.get("/api/v1/tickets/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Chamado não encontrado"


def test_create_ticket_rejects_short_title(authenticated_client):
    response = authenticated_client.post(
        "/api/v1/tickets",
        json={
            "title": "Erro",
            "description": "O sistema apresenta uma falha ao entrar.",
        },
    )

    assert response.status_code == 422


def test_create_ticket_rejects_short_description(authenticated_client):
    response = authenticated_client.post(
        "/api/v1/tickets",
        json={
            "title": "Erro ao acessar o sistema",
            "description": "Falha",
        },
    )

    assert response.status_code == 422


def test_update_ticket_status(authenticated_client):
    create_response = authenticated_client.post(
        "/api/v1/tickets",
        json={
            "title": "Erro ao acessar o sistema",
            "description": "O usuário não consegue entrar no painel.",
        },
    )

    ticket_id = create_response.json()["id"]

    response = authenticated_client.patch(
        f"/api/v1/tickets/{ticket_id}/status",
        json={"status": "in_progress"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"


def test_update_nonexistent_ticket_status(authenticated_client):
    response = authenticated_client.patch(
        "/api/v1/tickets/999/status",
        json={"status": "resolved"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Chamado não encontrado"


def test_update_ticket_with_invalid_status(authenticated_client):
    create_response = authenticated_client.post(
        "/api/v1/tickets",
        json={
            "title": "Erro ao acessar o sistema",
            "description": "O usuário não consegue entrar no painel.",
        },
    )

    ticket_id = create_response.json()["id"]

    response = authenticated_client.patch(
        f"/api/v1/tickets/{ticket_id}/status",
        json={"status": "closed"},
    )

    assert response.status_code == 422

def test_update_ticket_status_records_history(authenticated_client):
    create_response = authenticated_client.post(
        "/api/v1/tickets",
        json={
            "title": "Erro ao acessar o sistema",
            "description": "O usuário não consegue entrar no painel.",
        },
    )

    ticket_id = create_response.json()["id"]

    response = authenticated_client.patch(
        f"/api/v1/tickets/{ticket_id}/status",
        json={"status": "in_progress"},
    )

    assert response.status_code == 200

    # Este endpoint será implementado na próxima etapa.
    history_response = authenticated_client.get(
        f"/api/v1/tickets/{ticket_id}/history"
    )

    assert history_response.status_code == 200
    history = history_response.json()

    assert len(history) == 1
    assert history[0]["previous_status"] == "open"
    assert history[0]["new_status"] == "in_progress"


def test_same_status_does_not_create_duplicate_history(authenticated_client):
    create_response = authenticated_client.post(
        "/api/v1/tickets",
        json={
            "title": "Erro ao acessar o sistema",
            "description": "O usuário não consegue entrar no painel.",
        },
    )

    ticket_id = create_response.json()["id"]

    for _ in range(2):
        response = authenticated_client.patch(
            f"/api/v1/tickets/{ticket_id}/status",
            json={"status": "in_progress"},
        )
        assert response.status_code == 200

    history_response = authenticated_client.get(
        f"/api/v1/tickets/{ticket_id}/history"
    )

    assert history_response.status_code == 200
    history = history_response.json()

    assert len(history) == 1

def test_list_tickets_pagination(authenticated_client):
    for title in ["Chamado A", "Chamado B", "Chamado C"]:
        authenticated_client.post(
            "/api/v1/tickets",
            json={
                "title": title,
                "description": "Descrição do chamado para teste.",
            },
        )

    response = authenticated_client.get("/api/v1/tickets?page=1&limit=2")

    assert response.status_code == 200
    assert len(response.json()) == 2

    response = authenticated_client.get("/api/v1/tickets?page=2&limit=2")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_filter_tickets_by_status(authenticated_client):
    create_response = authenticated_client.post(
        "/api/v1/tickets",
        json={
            "title": "Chamado em andamento",
            "description": "Descrição para testar o filtro.",
        },
    )

    ticket_id = create_response.json()["id"]

    authenticated_client.patch(
        f"/api/v1/tickets/{ticket_id}/status",
        json={"status": "in_progress"},
    )

    response = authenticated_client.get("/api/v1/tickets?status=in_progress")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["status"] == "in_progress"


def test_search_tickets_by_title(authenticated_client):
    authenticated_client.post(
        "/api/v1/tickets",
        json={
            "title": "Erro no servidor principal",
            "description": "Problema de conexão.",
        },
    )

    response = authenticated_client.get("/api/v1/tickets?search=servidor")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert "servidor" in response.json()[0]["title"]


def test_search_tickets_by_description(authenticated_client):
    authenticated_client.post(
        "/api/v1/tickets",
        json={
            "title": "Falha de sistema",
            "description": "O banco de dados está indisponível.",
        },
    )

    response = authenticated_client.get("/api/v1/tickets?search=indisponível")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert "indisponível" in response.json()[0]["description"]


def test_sort_tickets_by_title(authenticated_client):
    for title in ["Zebra", "Abacaxi", "Macaco"]:
        authenticated_client.post(
            "/api/v1/tickets",
            json={
                "title": title,
                "description": "Descrição para teste de ordenação.",
            },
        )

    response = authenticated_client.get(
        "/api/v1/tickets?sort_by=title&sort_order=asc"
    )

    assert response.status_code == 200

    titles = [ticket["title"] for ticket in response.json()]

    assert titles == ["Abacaxi", "Macaco", "Zebra"]


def test_list_tickets_rejects_invalid_status(authenticated_client):
    response = authenticated_client.get("/api/v1/tickets?status=closed")

    assert response.status_code == 422


def test_list_tickets_rejects_invalid_pagination(authenticated_client):
    response = authenticated_client.get("/api/v1/tickets?page=0")

    assert response.status_code == 422

def test_create_ticket_with_high_priority(authenticated_client):
    response = authenticated_client.post(
        "/api/v1/tickets",
        json={
            "title": "Servidor indisponível",
            "description": "O servidor principal está fora do ar.",
            "priority": "high",
        },
    )

    assert response.status_code == 201
    assert response.json()["priority"] == "high"


def test_create_ticket_with_default_priority(authenticated_client):
    response = authenticated_client.post(
        "/api/v1/tickets",
        json={
            "title": "Dúvida sobre sistema",
            "description": "O usuário precisa de orientação.",
        },
    )

    assert response.status_code == 201
    assert response.json()["priority"] == "medium"


def test_create_ticket_with_critical_priority(authenticated_client):
    response = authenticated_client.post(
        "/api/v1/tickets",
        json={
            "title": "Sistema totalmente parado",
            "description": "Todos os usuários estão sem acesso.",
            "priority": "critical",
        },
    )

    assert response.status_code == 201
    assert response.json()["priority"] == "critical"


def test_create_ticket_rejects_invalid_priority(authenticated_client):
    response = authenticated_client.post(
        "/api/v1/tickets",
        json={
            "title": "Erro no sistema",
            "description": "O usuário não consegue acessar.",
            "priority": "urgent",
        },
    )

    assert response.status_code == 422

def test_create_ticket_with_hardware_category(authenticated_client):
    response = authenticated_client.post(
        "/api/v1/tickets",
        json={
            "title": "Problema no computador",
            "description": "O computador não está ligando.",
            "category": "hardware",
        },
    )

    assert response.status_code == 201
    assert response.json()["category"] == "hardware"


def test_create_ticket_with_software_category(authenticated_client):
    response = authenticated_client.post(
        "/api/v1/tickets",
        json={
            "title": "Erro no aplicativo",
            "description": "O aplicativo fecha inesperadamente.",
            "category": "software",
        },
    )

    assert response.status_code == 201
    assert response.json()["category"] == "software"


def test_create_ticket_with_network_category(authenticated_client):
    response = authenticated_client.post(
        "/api/v1/tickets",
        json={
            "title": "Problema na internet",
            "description": "A conexão está instável.",
            "category": "network",
        },
    )

    assert response.status_code == 201
    assert response.json()["category"] == "network"


def test_create_ticket_with_access_category(authenticated_client):
    response = authenticated_client.post(
        "/api/v1/tickets",
        json={
            "title": "Problema de login",
            "description": "O usuário não consegue acessar sua conta.",
            "category": "access",
        },
    )

    assert response.status_code == 201
    assert response.json()["category"] == "access"


def test_create_ticket_with_default_category(authenticated_client):
    response = authenticated_client.post(
        "/api/v1/tickets",
        json={
            "title": "Solicitação geral",
            "description": "O usuário precisa de atendimento.",
        },
    )

    assert response.status_code == 201
    assert response.json()["category"] == "other"


def test_create_ticket_rejects_invalid_category(authenticated_client):
    response = authenticated_client.post(
        "/api/v1/tickets",
        json={
            "title": "Problema no sistema",
            "description": "O usuário relatou um problema.",
            "category": "finance",
        },
    )

    assert response.status_code == 422


def test_open_ticket_can_move_to_in_progress(authenticated_client):
    ticket = authenticated_client.post(
        "/api/v1/tickets",
        json={
            "title": "Problema de acesso",
            "description": "O usuário não consegue entrar.",
        },
    ).json()

    response = authenticated_client.patch(
        f"/api/v1/tickets/{ticket['id']}/status",
        json={"status": "in_progress"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"


def test_in_progress_ticket_can_be_resolved(authenticated_client):
    ticket = authenticated_client.post(
        "/api/v1/tickets",
        json={
            "title": "Problema de acesso",
            "description": "O usuário não consegue entrar.",
        },
    ).json()

    authenticated_client.patch(
        f"/api/v1/tickets/{ticket['id']}/status",
        json={"status": "in_progress"},
    )

    response = authenticated_client.patch(
        f"/api/v1/tickets/{ticket['id']}/status",
        json={"status": "resolved"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "resolved"


def test_resolved_ticket_can_be_reopened(authenticated_client):
    ticket = authenticated_client.post(
        "/api/v1/tickets",
        json={
            "title": "Problema de acesso",
            "description": "O usuário não consegue entrar.",
        },
    ).json()

    authenticated_client.patch(
        f"/api/v1/tickets/{ticket['id']}/status",
        json={"status": "in_progress"},
    )

    authenticated_client.patch(
        f"/api/v1/tickets/{ticket['id']}/status",
        json={"status": "resolved"},
    )

    response = authenticated_client.patch(
        f"/api/v1/tickets/{ticket['id']}/status",
        json={"status": "in_progress"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"


def test_open_ticket_cannot_be_resolved_directly(authenticated_client):
    ticket = authenticated_client.post(
        "/api/v1/tickets",
        json={
            "title": "Problema de acesso",
            "description": "O usuário não consegue entrar.",
        },
    ).json()

    response = authenticated_client.patch(
        f"/api/v1/tickets/{ticket['id']}/status",
        json={"status": "resolved"},
    )

    assert response.status_code == 409
    assert "Não é permitido" in response.json()["detail"]


def test_in_progress_ticket_cannot_return_to_open(authenticated_client):
    ticket = authenticated_client.post(
        "/api/v1/tickets",
        json={
            "title": "Problema de acesso",
            "description": "O usuário não consegue entrar.",
        },
    ).json()

    authenticated_client.patch(
        f"/api/v1/tickets/{ticket['id']}/status",
        json={"status": "in_progress"},
    )

    response = authenticated_client.patch(
        f"/api/v1/tickets/{ticket['id']}/status",
        json={"status": "open"},
    )

    assert response.status_code == 409
    assert "Não é permitido" in response.json()["detail"]

def test_filter_tickets_by_priority(authenticated_client):
    authenticated_client.post(
        "/api/v1/tickets",
        json={
            "title": "Chamado urgente",
            "description": "Servidor completamente indisponível.",
            "priority": "critical",
        },
    )

    authenticated_client.post(
        "/api/v1/tickets",
        json={
            "title": "Chamado normal",
            "description": "Dúvida sobre utilização.",
            "priority": "low",
        },
    )

    response = authenticated_client.get("/api/v1/tickets?priority=critical")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["priority"] == "critical"


def test_filter_tickets_by_category(authenticated_client):
    authenticated_client.post(
        "/api/v1/tickets",
        json={
            "title": "Problema no computador",
            "description": "Computador não liga.",
            "category": "hardware",
        },
    )

    authenticated_client.post(
        "/api/v1/tickets",
        json={
            "title": "Erro no aplicativo",
            "description": "Aplicativo fecha sozinho.",
            "category": "software",
        },
    )

    response = authenticated_client.get("/api/v1/tickets?category=hardware")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["category"] == "hardware"


def test_filter_tickets_by_priority_and_category(authenticated_client):
    authenticated_client.post(
        "/api/v1/tickets",
        json={
            "title": "Falha crítica na rede",
            "description": "Rede completamente indisponível.",
            "priority": "critical",
            "category": "network",
        },
    )

    authenticated_client.post(
        "/api/v1/tickets",
        json={
            "title": "Falha comum na rede",
            "description": "Conexão apresenta lentidão.",
            "priority": "low",
            "category": "network",
        },
    )

    response = authenticated_client.get(
        "/api/v1/tickets?priority=critical&category=network"
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["priority"] == "critical"
    assert response.json()[0]["category"] == "network"


def test_list_tickets_rejects_invalid_priority_and_category(authenticated_client):
    response_priority = authenticated_client.get(
        "/api/v1/tickets?priority=urgent"
    )

    response_category = authenticated_client.get(
        "/api/v1/tickets?category=finance"
    )

    assert response_priority.status_code == 422
    assert response_category.status_code == 422


def test_ticket_history_returns_404_for_nonexistent_ticket(
    authenticated_client,
):
    response = authenticated_client.get(
        "/api/v1/tickets/99999/history"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Chamado não encontrado"



def test_review_nonexistent_triage_returns_404(
    authenticated_client,
):
    response = authenticated_client.patch(
        "/api/v1/tickets/99999/triages/99999/review",
        json={
            "review_status": "accepted",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Chamado ou análise não encontrado."
    )
