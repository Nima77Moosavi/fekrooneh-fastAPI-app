import os
import redis.asyncio as redis
from fastapi import HTTPException

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
LEADERBOARD_KEY = "leaderboard:global"


class LeaderboardService:
    def __init__(self):
        # create a connection per service instance
        self.r = redis.from_url(REDIS_URL, decode_responses=True)

    async def get_top_users(self, limit: int = 50):
        entries = await self.r.zrevrange(LEADERBOARD_KEY, 0, limit - 1, withscores=True)
        if not entries:
            raise HTTPException(status_code=404, detail="Leaderboard is empty")
        return [
            {"user": member, "xp": int(score)}
            for member, score in entries
        ]

    async def get_user_rank(self, user_id: str):
        rank = await self.r.zrevrank(LEADERBOARD_KEY, user_id)
        score = await self.r.zscore(LEADERBOARD_KEY, user_id)
        if rank is None:
            raise HTTPException(status_code=404, detail="User not found in leaderboard")
        return {"user": user_id, "rank": rank + 1, "xp": int(score)}

    async def close(self):
        await self.r.close()
