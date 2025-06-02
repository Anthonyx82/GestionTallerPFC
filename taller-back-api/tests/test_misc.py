import pytest

@pytest.mark.anyio
async def test_saludo(client):
    resp = await client.get("/saludo")
    assert resp.status_code == 200
    assert resp.json()["mensaje"] == "¡La API está funcionando correctamente!"

@pytest.mark.anyio
async def test_imagen_vehiculo(client):
    resp = await client.get("/car-imagery/", params={"searchTerm": "Mazda 3"})
    assert resp.status_code == 200
    assert "http" in resp.text or "xml" in resp.text  # La respuesta es XML
