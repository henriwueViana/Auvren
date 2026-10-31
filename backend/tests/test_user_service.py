
import pytest
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.schemas.users import UserCreateRequest
from app.services import user_service
from app.services.user_service import (
    EmailAlreadyRegistered,
    create_user,
    list_users,
)


def make_user_data(
    name="Usuário Teste",
    email="teste@example.com",
    password="SenhaSegura123",
):
    return UserCreateRequest(
        name=name,
        email=email,
        password=password,
    )


def create_organization(db_session, name="Organização Teste"):
    from app.models.organization import Organization

    organization = Organization(name=name)
    db_session.add(organization)
    db_session.commit()
    db_session.refresh(organization)

    return organization


def test_create_user_successfully(db_session):
    organization = create_organization(db_session)

    user = create_user(
        db_session,
        make_user_data(),
        organization.id,
    )

    assert user.id is not None
    assert user.organization_id == organization.id
    assert user.name == "Usuário Teste"
    assert user.email == "teste@example.com"
    assert user.role == "agent"
    assert user.is_active is True


def test_create_user_normalizes_and_trims_data(db_session):
    organization = create_organization(db_session)

    user = create_user(
        db_session,
        make_user_data(
            name="  Usuário Teste  ",
            email=" TESTE@EXAMPLE.COM ",
        ),
        organization.id,
    )

    assert user.name == "Usuário Teste"
    assert user.email == "teste@example.com"


def test_create_user_rejects_existing_email(db_session):
    organization = create_organization(db_session)
    data = make_user_data()

    create_user(db_session, data, organization.id)

    with pytest.raises(EmailAlreadyRegistered):
        create_user(db_session, data, organization.id)


def test_create_user_rolls_back_on_integrity_error(
    db_session,
    monkeypatch,
):
    organization = create_organization(db_session)

    def raise_integrity_error():
        raise IntegrityError(
            "INSERT INTO users",
            {},
            Exception("duplicate"),
        )

    monkeypatch.setattr(db_session, "commit", raise_integrity_error)

    with pytest.raises(EmailAlreadyRegistered):
        create_user(
            db_session,
            make_user_data(),
            organization.id,
        )

    assert db_session.query(User).count() == 0


def test_create_user_rolls_back_on_unexpected_error(
    db_session,
    monkeypatch,
):
    organization = create_organization(db_session)

    def raise_unexpected_error(password):
        raise RuntimeError("Erro inesperado")

    monkeypatch.setattr(
        user_service,
        "hash_password",
        raise_unexpected_error,
    )

    with pytest.raises(RuntimeError, match="Erro inesperado"):
        create_user(
            db_session,
            make_user_data(),
            organization.id,
        )

    assert db_session.query(User).count() == 0


def test_list_users_returns_organization_users(db_session):
    organization = create_organization(db_session)

    create_user(
        db_session,
        make_user_data(name="Carlos", email="carlos@example.com"),
        organization.id,
    )

    create_user(
        db_session,
        make_user_data(name="Ana", email="ana@example.com"),
        organization.id,
    )

    users = list_users(db_session, organization.id)

    assert len(users) == 2
    assert [user.name for user in users] == ["Ana", "Carlos"]


def test_list_users_does_not_return_other_organizations(db_session):
    organization_a = create_organization(db_session, "Organização A")
    organization_b = create_organization(db_session, "Organização B")

    create_user(
        db_session,
        make_user_data(email="a@example.com"),
        organization_a.id,
    )

    create_user(
        db_session,
        make_user_data(email="b@example.com"),
        organization_b.id,
    )

    users = list_users(db_session, organization_a.id)

    assert len(users) == 1
    assert users[0].email == "a@example.com"


def test_list_users_returns_empty_list_when_no_users(db_session):
    organization = create_organization(db_session)

    users = list_users(db_session, organization.id)

    assert users == []

def test_create_user_rolls_back_on_commit_error(
    db_session,
    monkeypatch,
):
    organization = create_organization(db_session)

    def raise_unexpected_error():
        raise RuntimeError("Falha inesperada no commit")

    monkeypatch.setattr(
        db_session,
        "commit",
        raise_unexpected_error,
    )

    with pytest.raises(
        RuntimeError,
        match="Falha inesperada no commit",
    ):
        create_user(
            db_session,
            make_user_data(),
            organization.id,
        )

    assert db_session.query(User).count() == 0
