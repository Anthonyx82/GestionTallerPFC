import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import Base, get_db, app
from fastapi_mail import FastMail
from unittest.mock import AsyncMock
from httpx import AsyncClient, ASGITransport

# Base de datos SQLite en memoria
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear tablas una vez para todos los tests
Base.metadata.create_all(bind=engine)

# Override de get_db para usar la base de datos en memoria
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Sobrescribimos la dependencia get_db de FastAPI
app.dependency_overrides[get_db] = override_get_db

# Patch para el sistema de correos
@pytest.fixture(autouse=True)
def mock_mail(monkeypatch):
    mock_fm = AsyncMock(spec=FastMail)
    monkeypatch.setattr("main.fm", mock_fm)

# Fixture para anyio backend (necesario para pytest-asyncio o anyio)
@pytest.fixture
def anyio_backend():
    return "asyncio"

# Fixture para el cliente HTTP async de FastAPI
@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
