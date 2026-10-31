from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.organization import Organization
from app.models.user import User
from app.schemas.auth import RegisterRequest


class EmailAlreadyRegistered(Exception):
    pass


def register_user(
    db: Session,
    data: RegisterRequest,
) -> User:
    email = str(data.email).strip().lower()

    existing_user = db.scalar(
        select(User).where(User.email == email)
    )

    if existing_user:
        raise EmailAlreadyRegistered(
            "Este e-mail já está cadastrado."
        )

    organization = Organization(
        name=data.organization_name.strip(),
    )

    try:
        db.add(organization)
        db.flush()

        user = User(
            organization_id=organization.id,
            name=data.name.strip(),
            email=email,
            hashed_password=hash_password(data.password),
            role="admin",
            is_active=True,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    except IntegrityError as exc:
        db.rollback()

        raise EmailAlreadyRegistered(
            "Este e-mail já está cadastrado."
        ) from exc

    except Exception:
        db.rollback()
        raise


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> User | None:
    normalized_email = email.strip().lower()

    user = db.scalar(
        select(User).where(User.email == normalized_email)
    )

    if user is None:
        return None

    if not user.is_active:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user