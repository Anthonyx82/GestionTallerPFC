import pytest

@pytest.mark.anyio
async def test_guardar_y_obtener_vehiculo(client):
    await client.post("/register", json={"username": "caruser", "password": "clave123"})
    login = await client.post("/login", json={"username": "caruser", "password": "clave123"})
    token = login.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    body = {
        "marca": "Toyota", "modelo": "Corolla", "year": 2020,
        "rpm": 1000, "velocidad": 60, "vin": "1HGCM82633A004352", "revision": {"oil": "ok"}
    }
    resp = await client.post("/guardar-vehiculo/", headers=headers, json=body)
    assert resp.status_code == 200
    vehiculo_id = resp.json()["id"]

    # Obtener lista
    resp2 = await client.get("/mis-vehiculos/", headers=headers)
    assert resp2.status_code == 200
    assert len(resp2.json()["vehiculos"]) == 1

    # Obtener uno
    resp3 = await client.get(f"/mis-vehiculos/{vehiculo_id}", headers=headers)
    assert resp3.status_code == 200
    assert resp3.json()["vin"] == "1HGCM82633A004352"

    # Editar
    resp4 = await client.put(f"/editar-vehiculo/{vehiculo_id}", headers=headers, json={
        "marca": "Honda", "modelo": "Civic", "year": 2021,
        "rpm": 1200, "velocidad": 80, "vin": "1HGCM82633A004352"
    })
    assert resp4.status_code == 200

    # Eliminar
    resp5 = await client.delete(f"/eliminar-vehiculo/{vehiculo_id}", headers=headers)
    assert resp5.status_code == 200
