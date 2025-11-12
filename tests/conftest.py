import asyncio
import os
import pytest_asyncio
from httpx import AsyncClient
from httpx import ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from unittest.mock import AsyncMock, patch
import redis.asyncio as redis

# ---------------------------
# 1️⃣ Async Test Client
# ---------------------------
@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


# ---------------------------
# 2️⃣ Temporary Test Database
# ---------------------------

TEST_DATABASE_URL = "postgresql+asyncpg://nima:secret123@localhost:5433/test_db"


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        # Drop all tables first (just in case) and recreate
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def test_db_session(test_engine):
    async_session = sessionmaker(
        test_engine, expire_on_commit=False, class_=AsyncSession
    )
    async with async_session() as session:
        # Override FastAPI dependency
        async def _get_test_session():
            yield session

        app.dependency_overrides[get_db] = _get_test_session
        yield session
        await session.rollback()  # rollback after each test


# ---------------------------
# 3️⃣ Mock Redis
# ---------------------------

@pytest_asyncio.fixture
async def mock_redis():
    mock = AsyncMock(spec=redis.Redis)
    # Patch the redis.from_url to return this mock
    with patch("app.events.redis.from_url", return_value=mock):
        yield mock
