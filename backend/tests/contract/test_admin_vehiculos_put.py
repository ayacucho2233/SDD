import uuid

import pytest

pytestmark = pytest.mark.asyncio


async def test_modificar_vehiculo_es_200(client, admin_auth, vehiculo_activo):
    response = await client.put(
        f"/admin/vehiculos/{vehiculo_activo.id}",
        json={"patente": "ZZ000ZZ", "tipo": "camioneta"},
        auth=admin_auth,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["patente"] == "ZZ000ZZ"
    assert body["tipo"] == "camioneta"


async def test_modificar_vehiculo_tipo_invalido_es_400(client, admin_auth, vehiculo_activo):
    response = await client.put(
        f"/admin/vehiculos/{vehiculo_activo.id}",
        json={"patente": vehiculo_activo.patente, "tipo": "moto"},
        auth=admin_auth,
    )

    assert response.status_code in (400, 422)


async def test_modificar_vehiculo_sin_credenciales_es_401(client, vehiculo_activo):
    response = await client.put(
        f"/admin/vehiculos/{vehiculo_activo.id}", json={"patente": "ZZ000ZZ", "tipo": "auto"}
    )

    assert response.status_code == 401


async def test_modificar_vehiculo_inexistente_es_404(client, admin_auth):
    response = await client.put(
        f"/admin/vehiculos/{uuid.uuid4()}", json={"patente": "ZZ000ZZ", "tipo": "auto"}, auth=admin_auth
    )

    assert response.status_code == 404


async def test_modificar_vehiculo_patente_duplicada_es_409(client, admin_auth, vehiculo_activo, db_session):
    from app.repositories.vehiculo_repository import VehiculoRepository

    otro = await VehiculoRepository(db_session).create(patente="OT999RO", tipo="auto")

    response = await client.put(
        f"/admin/vehiculos/{otro.id}",
        json={"patente": vehiculo_activo.patente, "tipo": "auto"},
        auth=admin_auth,
    )

    assert response.status_code == 409
