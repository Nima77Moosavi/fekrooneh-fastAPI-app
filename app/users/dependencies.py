from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from .repositories import UserRepository
from .services import UserService

def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """
    Dependency provider for UserService.
    Wires together DB session -> UserRepository -> UserService.
    """
    repo = UserRepository(db)
    return UserService(repo)
