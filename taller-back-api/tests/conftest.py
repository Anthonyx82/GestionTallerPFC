import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import Base, get_db, app
from fastapi_mail import FastMail, ConnectionConfig
from unittest.mock import AsyncMock
from httpx import AsyncClient, ASGITransport

# Base de datos SQLite en memoria
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine)

# Crear tablas una vez para todos los tests
Base.metadata.create_all(bind=engine)

# Override de get_db
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Usamos esta base temporal en lugar de MySQL
app.dependency_overrides[get_db] = override_get_db

# Patch para el sistema de correos
@pytest.fixture(autouse=True)
def mock_mail(monkeypatch):
    mock_fm = AsyncMock(spec=FastMail)
    monkeypatch.setattr("main.fm", mock_fm)

# Fixture para cliente HTTP
@pytest.fixture
def anyio_backend():
    return "asyncio"

@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
