"""
功能1 测试：用户注册登录

运行：pytest tests/ -v
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.main import app
from app.database import Base
from app.deps import get_db

# 测试用 SQLite（不污染开发数据库）
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
test_engine = create_async_engine(TEST_DATABASE_URL)
TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)


async def override_get_db():
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    """每个测试前建表，测试后删表"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = override_get_db
    return app


@pytest.mark.asyncio
async def test_register(client):
    async with AsyncClient(transport=ASGITransport(app=client), base_url="http://test") as ac:
        resp = await ac.post("/auth/register", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "123456",
        })
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "testuser"
    assert "hashed_password" not in data   # 密码不能泄露


@pytest.mark.asyncio
async def test_login(client):
    async with AsyncClient(transport=ASGITransport(app=client), base_url="http://test") as ac:
        # 先注册
        await ac.post("/auth/register", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "123456",
        })
        # 再登录
        resp = await ac.post("/auth/login", json={
            "username": "testuser",
            "password": "123456",
        })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    async with AsyncClient(transport=ASGITransport(app=client), base_url="http://test") as ac:
        await ac.post("/auth/register", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "123456",
        })
        resp = await ac.post("/auth/login", json={
            "username": "testuser",
            "password": "wrong",
        })
    assert resp.status_code == 401
