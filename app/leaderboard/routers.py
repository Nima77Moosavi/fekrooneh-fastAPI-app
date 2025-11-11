from fastapi import APIRouter, Depends
from app.leaderboard.services import LeaderboardService

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])

async def get_service():
    service = LeaderboardService()
    try:
        yield service
    finally:
        await service.close()

@router.get("/")
async def get_leaderboard(limit: int = 50, service: LeaderboardService = Depends(get_service)):
    return await service.get_top_users(limit)

@router.get("/user/{user_id}")
async def get_user_rank(user_id: str, service: LeaderboardService = Depends(get_service)):
    return await service.get_user_rank(user_id)
