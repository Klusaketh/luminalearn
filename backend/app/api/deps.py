import uuid
from collections.abc import AsyncGenerator, Callable
from typing import Any

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.core.redis import redis_client
from app.core.security import decode_token
from app.models.user import User, UserRole
from app.repositories.user_repository import user_repository

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI Dependency yielding Async SQLAlchemy Session."""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_redis() -> Any:
    """FastAPI Dependency yielding Redis client."""
    return redis_client


async def get_current_user(
    request: Request,
    token: str | None = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Extract Authorization Bearer token from Header or Cookie, decode payload,
    and retrieve User from database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials or token expired.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Fallback to HTTP-only cookie if header is absent
    if not token:
        token = request.cookies.get("access_token")

    if not token:
        raise credentials_exception

    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise credentials_exception
        user_id_str: str | None = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise credentials_exception

    user = await user_repository.get_by_id(db, user_id=user_id)
    if user is None:
        raise credentials_exception

    return user


async def user_from_access_token(db: AsyncSession, token: str | None) -> User | None:
    """
    Resolve an active, verified user from an access token without raising.
    Used where an HTTP exception cannot be raised (the voice WebSocket handshake):
    None means the session must be refused.
    """
    if not token:
        return None
    try:
        payload = decode_token(token)
    except jwt.PyJWTError:
        return None
    if payload.get("type") != "access":
        return None
    try:
        user_id = uuid.UUID(str(payload.get("sub")))
    except ValueError:
        return None
    user = await user_repository.get_by_id(db, user_id=user_id)
    if user is None or not user.is_active or not user.is_verified:
        return None
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Validate that current authenticated user account is active and email verified."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account."
        )
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="EMAIL_VERIFICATION_REQUIRED"
        )
    return current_user


def require_role(allowed_roles: list[UserRole | str]) -> Callable:
    """
    Dependency factory checking if current user possesses one of the allowed roles.
    Example usage: Depends(require_role([UserRole.ADMIN, UserRole.TEACHER]))
    """
    role_strings = [r.value if isinstance(r, UserRole) else r for r in allowed_roles]

    async def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role.value not in role_strings:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Requires one of roles: {role_strings}"
            )
        return current_user

    return role_checker
