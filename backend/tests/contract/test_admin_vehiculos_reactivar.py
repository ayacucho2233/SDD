import uuid

import pytest

pytestmark = pytest.mark.asyncio


async def test_reactivar_desde_baja_temporal_es_200(client, admin_auth, vehiculo_activo):
    await client.post(f"/admin/vehiculos/{vehiculo_activo.id}/baja-temporal", auth=admin_auth)

    response = await client.post(
        f"/admin/vehiculos/{vehiculo_activo.id}/reactivar", auth=admin_auth
    )

    assert response.status_code == 200
    assert response.json()["estado"] == "activo"


async def test_reactivar_sin_credenciales_es_401(client, vehiculo_activo):
    response = await client.post(f"/admin/vehiculos/{vehiculo_activo.id}/reactivar")

    assert response.status_code == 401


async def test_reactivar_vehiculo_inexistente_es_404(client, admin_auth):
    response = await client.post(f"/admin/vehiculos/{uuid.uuid4()}/reactivar", auth=admin_auth)

    assert response.status_code == 404


async def test_reactivar_desde_baja_definitiva_es_409(client, admin_auth, vehiculo_activo):
    await client.post(f"/admin/vehiculos/{vehiculo_activo.id}/baja-definitiva", auth=admin_auth)

    response = await client.post(
        f"/admin/vehiculos/{vehiculo_activo.id}/reactivar", auth=admin_auth
    )

    assert response.status_code == 409
