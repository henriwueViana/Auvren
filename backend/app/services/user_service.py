from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.schemas.users import UserCreateRequest


class EmailAlreadyRegistered(Exception):
    pass


def create_user(
    db: Session,
    data: UserCreateRequest,
    organization_id: int,
) -> User:
    email = str(data.email).strip().lower()

    existing_user = db.scalar(
        select(User).where(User.email == email)
    )

    if existing_user:
        raise EmailAlreadyRegistered(
            "Este e-mail já está cadastrado."
        )

    user = User(
        organization_id=organization_id,
        name=data.name.strip(),
        email=email,
        hashed_password=hash_password(data.password),
        role="agent",
        is_active=True,
    )

    try:
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


def list_users(
    db: Session,
    organization_id: int,
) -> list[User]:
    statement = (
        select(User)
        .where(User.organization_id == organization_id)
        .order_by(User.name.asc())
    )

    return list(db.scalars(statement).all())
