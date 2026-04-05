from uuid import UUID

from sqlalchemy import and_, func, select, true, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    """Data access layer for User operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ──────────────────────────────────────
    # Create
    # ──────────────────────────────────────

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

    # ──────────────────────────────────────
    # Read
    # ──────────────────────────────────────

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

    async def list_users(
        self,
        role: str | None = None,
        is_active: bool | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[User], int]:
        """
        List users with optional filtering by role and status.
        Returns (users, total_count) for pagination.
        """
        conditions = []

        if role is not None:
            conditions.append(User.role == role)
        if is_active is not None:
            conditions.append(User.is_active == is_active)

        where_clause = and_(*conditions) if conditions else true()

        # Get total count
        count_query = select(func.count()).select_from(User).where(where_clause)
        total = (await self.db.execute(count_query)).scalar()

        # Get paginated results
        query = (
            select(User)
            .where(where_clause)
            .order_by(User.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(query)
        users = list(result.scalars().all())
        return users, 0 if total is None else total

    # ──────────────────────────────────────
    # Update
    # ──────────────────────────────────────

    async def update_role(self, user_id: UUID, role: str) -> User | None:
        """Update a user's role. Returns updated user or None if not found"""
        await self.db.execute(update(User).where(User.id == user_id).values(role=role))
        await self.db.flush()
        return await self.get_by_id(user_id)

    async def update_status(self, user_id: UUID, is_active: bool) -> User | None:
        """Activate or deactivate a user. Returns updated user or None if not found"""
        await self.db.execute(
            update(User).where(User.id == user_id).values(is_active=is_active)
        )
        await self.db.flush()
        return await self.get_by_id(user_id)
