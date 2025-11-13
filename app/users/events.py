import json
import os
from datetime import datetime
import redis.asyncio as redis

# Get Redis URL from environment, fallback to local default
REDIS_URL = os.getenv("REDIS_URL", "redis://redis-server:6379")
LEADERBOARD_STREAM = "leaderboard_events"
LEADERBOARD_KEY = "leaderboard:global"

async def clear_leaderboard():
    r = redis.from_url(REDIS_URL, decode_responses=True)
    deleted = await r.delete(LEADERBOARD_KEY)
    await r.aclose()
    print(f"✅ Cleared leaderboard ({deleted} key(s) removed).")

async def publish_leaderboard_event(
    event_type: str,
    user_id: int,
    xp: int,
    streak: int | None = None
):
    """Publish leaderboard-related events (user_created, checkin)."""
    r = redis.from_url(REDIS_URL, decode_responses=True)
    event = {
        "event": event_type,
        "user_id": user_id,
        "xp": xp,
        "timestamp": datetime.utcnow().isoformat(),
    }
    if streak is not None:
        event["streak"] = streak

    await r.xadd(LEADERBOARD_STREAM, event)
    await r.aclose()
