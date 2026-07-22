import pytest

pytestmark = pytest.mark.asyncio


async def test_alta_vehiculo_valido_es_201(client, admin_auth):
    response = await client.post(
        "/admin/vehiculos", json={"patente": "XY999ZZ", "tipo": "camioneta"}, auth=admin_auth
    )

    assert response.status_code == 201
    body = response.json()
    assert body["estado"] == "activo"


async def test_alta_vehiculo_tipo_invalido_es_400(client, admin_auth):
    response = await client.post(
        "/admin/vehiculos", json={"patente": "AA111BB", "tipo": "moto"}, auth=admin_auth
    )

    assert response.status_code in (400, 422)


async def test_alta_vehiculo_sin_credenciales_es_401(client):
    response = await client.post("/admin/vehiculos", json={"patente": "CC222DD", "tipo": "auto"})

    assert response.status_code == 401


async def test_alta_vehiculo_patente_duplicada_es_409(client, admin_auth, vehiculo_activo):
    response = await client.post(
        "/admin/vehiculos",
        json={"patente": vehiculo_activo.patente, "tipo": "auto"},
        auth=admin_auth,
    )

    assert response.status_code == 409
