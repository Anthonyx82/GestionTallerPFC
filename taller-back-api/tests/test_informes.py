import pytest

@pytest.mark.anyio
async def test_crear_y_ver_informe(client):
    await client.post("/register", json={"username": "informeuser", "password": "clave123"})
    login = await client.post("/login", json={"username": "informeuser", "password": "clave123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    vehiculo = await client.post("/guardar-vehiculo/", headers=headers, json={
        "marca": "Ford", "modelo": "Fiesta", "year": 2019,
        "rpm": 900, "velocidad": 70, "vin": "1FAFP34N95W000000",
        "revision": {"brakes": "worn"}
    })
    id_vehiculo = vehiculo.json()["id"]

    informe = await client.post(f"/crear-informe/{id_vehiculo}", headers=headers, json={"email": "test@correo.com"})
    assert informe.status_code == 200
    token_informe = informe.json()["token"]

    ver_informe = await client.get(f"/informe/{token_informe}")
    assert ver_informe.status_code == 200
    assert "vehiculo" in ver_informe.json()
