import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole, VARKModality


class UserRepository:
    """Async UserRepository handling database operations for User entity."""

    async def get_by_id(self, db: AsyncSession, user_id: uuid.UUID) -> User | None:
        """Fetch user by primary key UUID."""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        """Fetch user by email address."""
        result = await db.execute(select(User).where(User.email == email.lower()))
        return result.scalars().first()

    async def create(
        self,
        db: AsyncSession,
        *,
        email: str,
        password_hash: str,
        full_name: str,
        role: UserRole = UserRole.STUDENT,
        preferred_modality: VARKModality = VARKModality.VISUAL,
        is_verified: bool = False
    ) -> User:
        """Create a new user record."""
        user = User(
            email=email.lower(),
            password_hash=password_hash,
            full_name=full_name,
            role=role,
            preferred_modality=preferred_modality,
            is_active=True,
            is_verified=is_verified
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def update_password(self, db: AsyncSession, user: User, password_hash: str) -> User:
        """Update password hash for a user."""
        user.password_hash = password_hash
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def update_active_status(self, db: AsyncSession, user: User, is_active: bool) -> User:
        """Update user active status."""
        user.is_active = is_active
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def update_verified_status(self, db: AsyncSession, user: User, is_verified: bool) -> User:
        """Update user verified status."""
        user.is_verified = is_verified
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user


user_repository = UserRepository()
