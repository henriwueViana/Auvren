from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.models.user import User
from app.schemas.users import UserCreateRequest, UserListResponse
from app.services.user_service import (
    EmailAlreadyRegistered,
    create_user,
    list_users,
)

router = APIRouter(prefix="/api/v1/users", tags=["Usuários"])


@router.post(
    "",
    response_model=UserListResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user_endpoint(
    data: UserCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    try:
        return create_user(
            db=db,
            data=data,
            organization_id=current_user.organization_id,
        )
    except EmailAlreadyRegistered as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.get(
    "",
    response_model=list[UserListResponse],
)
def list_users_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    return list_users(
        db=db,
        organization_id=current_user.organization_id,
    )
