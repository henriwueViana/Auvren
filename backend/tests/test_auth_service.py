
import pytest
from sqlalchemy.exc import IntegrityError

from app.models.organization import Organization
from app.models.user import User
from app.schemas.auth import RegisterRequest
from app.services import auth_service
from app.services.auth_service import (
    EmailAlreadyRegistered,
    authenticate_user,
    register_user,
)


def make_register_data(
    organization_name="Organização Teste",
    name="Usuário Teste",
    email="teste@example.com",
    password="SenhaSegura123",
):
    return RegisterRequest(
        organization_name=organization_name,
        name=name,
        email=email,
        password=password,
    )


def test_register_user_normalizes_and_trims_data(db_session):
    data = make_register_data(
        organization_name="  Organização Teste  ",
        name="  Usuário Teste  ",
        email=" TESTE@EXAMPLE.COM ",
    )

    user = register_user(db_session, data)

    assert user.email == "teste@example.com"
    assert user.name == "Usuário Teste"

    organization = db_session.get(Organization, user.organization_id)
    assert organization.name == "Organização Teste"
    assert user.role == "admin"
    assert user.is_active is True


def test_register_user_rejects_existing_email(db_session):
    data = make_register_data()

    register_user(db_session, data)

    with pytest.raises(EmailAlreadyRegistered):
        register_user(db_session, data)


def test_register_user_rolls_back_on_integrity_error(
    db_session,
    monkeypatch,
):
    def raise_integrity_error():
        raise IntegrityError(
            "INSERT INTO users",
            {},
            Exception("duplicate"),
        )

    monkeypatch.setattr(db_session, "commit", raise_integrity_error)

    with pytest.raises(EmailAlreadyRegistered):
        register_user(db_session, make_register_data())

    assert db_session.query(Organization).count() == 0
    assert db_session.query(User).count() == 0


def test_register_user_rolls_back_on_unexpected_error(
    db_session,
    monkeypatch,
):
    def raise_unexpected_error(password):
        raise RuntimeError("Erro inesperado")

    monkeypatch.setattr(
        auth_service,
        "hash_password",
        raise_unexpected_error,
    )

    with pytest.raises(RuntimeError, match="Erro inesperado"):
        register_user(db_session, make_register_data())

    assert db_session.query(Organization).count() == 0
    assert db_session.query(User).count() == 0


def test_authenticate_user_returns_none_when_user_does_not_exist(
    db_session,
):
    result = authenticate_user(
        db_session,
        "inexistente@example.com",
        "SenhaSegura123",
    )

    assert result is None


def test_authenticate_user_returns_none_when_user_is_inactive(
    db_session,
):
    user = register_user(
        db_session,
        make_register_data(),
    )

    user.is_active = False
    db_session.commit()

    result = authenticate_user(
        db_session,
        user.email,
        "SenhaSegura123",
    )

    assert result is None


def test_authenticate_user_returns_none_with_wrong_password(
    db_session,
):
    user = register_user(
        db_session,
        make_register_data(),
    )

    result = authenticate_user(
        db_session,
        user.email,
        "SenhaErrada123",
    )

    assert result is None


def test_authenticate_user_accepts_valid_credentials(db_session):
    user = register_user(
        db_session,
        make_register_data(),
    )

    result = authenticate_user(
        db_session,
        "  TESTE@EXAMPLE.COM  ",
        "SenhaSegura123",
    )

    assert result is not None
    assert result.id == user.id
