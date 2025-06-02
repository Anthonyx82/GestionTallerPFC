import pytest

@pytest.mark.anyio
async def test_guardar_errores(client):
    await client.post("/register", json={"username": "erroruser", "password": "clave123"})
    login = await client.post("/login", json={"username": "erroruser", "password": "clave123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    vehiculo = await client.post("/guardar-vehiculo/", headers=headers, json={
        "marca": "Mazda", "modelo": "3", "year": 2022, "rpm": 1000, "velocidad": 80,
        "vin": "JH4KA8260MC000000", "revision": {"oil": "low"}
    })
    id_vehiculo = vehiculo.json()["id"]

    errores = await client.post("/guardar-errores/", headers=headers, json={
        "vehiculo_id": id_vehiculo, "codigo_dtc": ["P0300", "P0420"]
    })
    assert errores.status_code == 200

    consult = await client.get(f"/mis-errores/{id_vehiculo}", headers=headers)
    assert consult.status_code == 200
    assert len(consult.json()) == 2
