import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.main import app
from app.core.database import get_session
from app.core.limiter import limiter

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

test_session_factory = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)

async def override_get_session():
    async with test_session_factory() as session:
        yield session

@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    app.dependency_overrides[get_session] = override_get_session
    
    limiter.enabled = False

    yield

    limiter.enabled = True
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac

@pytest_asyncio.fixture
async def auth_client(client):
    await client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "test1234"
    })

    response = await client.post("/auth/login", data={
        "username": "testuser",
        "password": "test1234"
    })

    token = response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client