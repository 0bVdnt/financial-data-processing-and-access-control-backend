import math
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.rbac import RequireRole
from app.models.user import User
from app.schemas.common import ApiResponse, Meta
from app.schemas.user import (
    Role,
    UpdateUserRoleRequest,
    UpdateUserStatusRequest,
    UserListParams,
    UserResponse,
)
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["User Management"])


@router.get(
    "/",
    response_model=ApiResponse[list[UserResponse]],
    summary="List all users (Admin only)",
    description=(
        "Retrieve a paginated list of all users. "
        "Supports filtering by role and active status."
    ),
)
async def list_users(
    role: Role | None = Query(None, description="Filter by role"),
    is_active: bool | None = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(RequireRole(Role.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    params = UserListParams(
        role=role,
        is_active=is_active,
        page=page,
        per_page=per_page,
    )

    service = UserService(db)
    users, total = await service.list_users(params)

    return ApiResponse(
        success=True,
        data=[UserResponse.model_validate(u) for u in users],
        meta=Meta(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=math.ceil(total / per_page) if total > 0 else 0,
        ),
    )


@router.get(
    "/{user_id}",
    response_model=ApiResponse[UserResponse],
    summary="Get a user by ID (Admin only)",
    description="Retrieve details of a specific user.",
)
async def get_user(
    user_id: UUID,
    current_user: User = Depends(RequireRole(Role.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    user = await service.get_user(user_id)
    return ApiResponse(success=True, data=UserResponse.model_validate(user))


@router.patch(
    "/{user_id}/role",
    response_model=ApiResponse[UserResponse],
    summary="Update a user's role (Admin only)",
    description=(
        "Change a user's role to viewer, analyst, or admin. "
        "Admins cannot change their own role to prevent lockout."
    ),
)
async def update_user_role(
    user_id: UUID,
    data: UpdateUserRoleRequest,
    current_user: User = Depends(RequireRole(Role.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    updated_user = await service.update_role(user_id, data, current_user)
    return ApiResponse(success=True, data=UserResponse.model_validate(updated_user))


@router.patch(
    "/{user_id}/status",
    response_model=ApiResponse[UserResponse],
    summary="Activate or deactivate a user (Admin only)",
    description=(
        "Set a user's active status. Deactivated users cannot log in "
        "or access any endpoints. Admins cannot deactivate themselves."
    ),
)
async def update_user_status(
    user_id: UUID,
    data: UpdateUserStatusRequest,
    current_user: User = Depends(RequireRole(Role.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    updated_user = await service.update_status(user_id, data, current_user)
    return ApiResponse(success=True, data=UserResponse.model_validate(updated_user))
