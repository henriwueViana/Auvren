
import os

os.environ["RATE_LIMIT_ENABLED"] = "false"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models import Organization, User, Ticket, TicketStatusHistory


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def authenticated_client(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "organization_name": "Organização de Testes",
            "name": "Usuário de Teste",
            "email": "teste@au vren.com".replace(" ", ""),
            "password": "SenhaSegura123",
        },
    )

    assert response.status_code == 201, response.text

    token = response.json()["access_token"]

    client.headers.update({
        "Authorization": f"Bearer {token}"
    })

    return client




@pytest.fixture
def db_session(client):
    override_get_db = app.dependency_overrides[get_db]
    db = next(override_get_db())

    try:
        yield db
    finally:
        db.close()


