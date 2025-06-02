import pytest

@pytest.mark.anyio
async def test_register_usuario(client):
    resp = await client.post("/register", json={"username": "usuario1", "password": "clave123"})
    assert resp.status_code == 200
    assert "mensaje" in resp.json()

@pytest.mark.anyio
async def test_login_usuario(client):
    # Primero registra
    await client.post("/register", json={"username": "usuario2", "password": "clave123"})
    # Luego login
    resp = await client.post("/login", json={"username": "usuario2", "password": "clave123"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()
