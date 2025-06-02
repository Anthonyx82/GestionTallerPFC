import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import Base, get_db, app
from fastapi_mail import FastMail
from unittest.mock import AsyncMock
from httpx import AsyncClient, ASGITransport
import os

# Configura la URL para usar una base SQLite en disco, así todas las conexiones
# comparten la misma base de datos durante los tests.
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Crea el motor de base de datos con conexión para múltiples threads (check_same_thread=False)
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Crea la sesión local para SQLAlchemy usando el engine creado.
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Sobrescribe la dependencia get_db en FastAPI para que use esta sesión de test.
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
        db.commit()  # Hace commit explícito para guardar los cambios realizados durante el test.
    finally:
        db.close()  # Cierra la sesión siempre para liberar recursos.

app.dependency_overrides[get_db] = override_get_db

# Fixture automático que parchea FastMail para evitar envíos reales de correos en tests.
@pytest.fixture(autouse=True)
def mock_mail(monkeypatch):
    mock_fm = AsyncMock(spec=FastMail)  # Creamos un mock asíncrono de FastMail.
    monkeypatch.setattr("main.fm", mock_fm)  # Reemplazamos la instancia original con el mock.

# Fixture automático para limpiar la base de datos antes de cada test,
# eliminando todas las tablas y creándolas desde cero.
@pytest.fixture(autouse=True)
def clear_db():
    Base.metadata.drop_all(bind=engine)  # Borra todas las tablas.
    Base.metadata.create_all(bind=engine)  # Crea las tablas nuevas limpias.

# Configuración para usar el backend asyncio con pytest-anyio para tests asíncronos.
@pytest.fixture
def anyio_backend():
    return "asyncio"

# Fixture para proveer un cliente HTTP asíncrono para probar la API FastAPI sin necesidad de servidor.
@pytest.fixture
async def client():
    transport = ASGITransport(app=app)  # Transporta las peticiones directamente a la app sin salir del proceso.
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac  # Provee el cliente para usar en los tests.

# Fixture para limpiar el archivo de base de datos SQLite al final de toda la sesión de tests.
# Evita acumular archivos de test viejos en el sistema.
@pytest.fixture(scope="session", autouse=True)
def cleanup():
    yield
    try:
        os.remove("test.db")
    except FileNotFoundError:
        pass  # Si no existe el archivo, no hace nada.
