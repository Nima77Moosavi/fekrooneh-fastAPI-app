from datetime import date


from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException


from .models import User
from .schemas import UserCreate, UserUpdate
from .repositories import UserRepository
from app.users.events import publish_leaderboard_event


class UserService:
    """
    Service layer for User operations.
    Encapsulates business logic and delegates persistence to UserRepository.
    """

    def __init__(self, repo: UserRepository):
        self.repo = repo

    @classmethod
    def with_session(cls, db: AsyncSession) -> "UserService":
        """
        Convenience constructor if you want to build the service directly
        from a database session (used in dependency injection).
        """
        return cls(UserRepository(db))

    async def register_user(self, payload: UserCreate) -> User:
        """
        Create a new user.
        Business rules (e.g., password hashing, uniqueness checks) can be added here.
        """
        # check if username exists
        existing = await self.repo.get_by_username(payload.username)
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Username already exists"
            )
        user = await self.repo.create(payload)

        # publish leaderboard event
        await publish_leaderboard_event(
            event_type="user_created",
            user_id=user.id,
            xp=user.xp,
            streak=user.streak,
        )

        return user

    async def find_user_by_id(self, user_id: int) -> User | None:
        """
        Retrieve a user by their ID.
        """
        return await self.repo.get_by_id(user_id)

    async def find_user_by_username(self, username: str) -> User | None:
        """
        Retrieve a user by their username.
        """
        return await self.repo.get_by_username(username)

    async def update_user(self, user: User, payload: UserUpdate) -> User:
        """
        Update user fields with provided payload.
        """
        return await self.repo.update(user, payload)

    async def delete_user(self, user: User) -> User:
        """
        Delete a user from the database.
        """
        return await self.repo.delete(user)
    
    async def sync_all_users_to_redis(self) -> int:
        """
        Publish all users to Redis for leaderboard sync.
        Returns the number of users synced.
        """
        users = await self.repo.list_all()  # implement list_all in UserRepository
        for user in users:
            await publish_leaderboard_event(
                event_type="sync_user",
                user_id=user.id,
                xp=user.xp,
                streak=user.streak,
            )
        return len(users)

    async def checkin(self, username: str) -> User:
        """
        Daily check-in logic:
        - Updates streaks, XP, and frozen days.
        - Publishes event to Redis.
        """
        user = await self.repo.get_by_username(username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        today = date.today()

        # Already checked in today
        if user.last_checkin == today:
            raise HTTPException(
                status_code=400, detail="Already checked in today")

        if not user.last_checkin:
            # First ever check-in
            user.streak = 1
        else:
            delta = (today - user.last_checkin).days
            if delta == 1:
                # Consecutive day
                user.streak += 1
            elif delta > 1:
                missed_days = delta - 1
                if user.frozen_days >= missed_days:
                    # Use frozen days to maintain streak
                    user.frozen_days -= missed_days
                    user.streak += 1
                else:
                    # Not enough frozen days → reset streak
                    user.streak = 1
                    user.frozen_days = 0

        # Update max streak
        if user.streak > user.max_streak:
            user.max_streak = user.streak

        # Add XP
        user.xp += 10

        # Update last_checkin date
        user.last_checkin = today

        # Save changes using repository
        self.repo.db.add(user)
        await self.repo.db.commit()
        await self.repo.db.refresh(user)

        # Publish event to Redis
        await publish_leaderboard_event(
            event_type="checkin",
            user_id=user.id,
            xp=user.xp,
            streak=user.streak
        )

        return user
