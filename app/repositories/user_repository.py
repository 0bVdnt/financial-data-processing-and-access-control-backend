from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    """Data access layer for User operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        email: str,
        password_hash: str,
        full_name: str,
        role: str = "viewer",
    ) -> User:
        """Insert a new user and return it"""
        user = User(
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            role=role,
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def get_by_id(self, user_id: UUID) -> User | None:
        """Fetch a user by their ID"""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Fetch user by their email address"""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def email_exists(self, email: str) -> bool:
        """Check if an email already exists"""
        user = await self.get_by_email(email)
        return user is not None
