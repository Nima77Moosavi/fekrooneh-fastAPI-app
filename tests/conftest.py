import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
import redis.asyncio as redis

TEST_DATABASE_URL = "postgresql+asyncpg://nima:secret123@test_db:5432/test_db"
TEST_REDIS_URL = "redis://redis:6379"

# ---------------------------
# DB engine (module scoped)
# ---------------------------
@pytest.fixture(scope="module")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

# ---------------------------
# DB session per test
# ---------------------------
@pytest.fixture
async def test_db_session(test_engine):
    async_session = sessionmaker(
        test_engine, expire_on_commit=False, class_=AsyncSession
    )
    async with async_session() as session:

        async def override_get_db():
            yield session

        app.dependency_overrides[get_db] = override_get_db
        yield session
        await session.rollback()
        app.dependency_overrides.clear()

# ---------------------------
# Real Redis client
# ---------------------------
@pytest.fixture
async def redis_client():
    client = redis.Redis.from_url(TEST_REDIS_URL, decode_responses=True)
    yield client
    await client.flushall()
    await client.aclose()  # <-- use aclose() to avoid deprecation warning

# ---------------------------
# Async client
# ---------------------------
@pytest.fixture
async def async_client(test_db_session, redis_client):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client
    await client.aclose()  # <-- use aclose() instead of close()
