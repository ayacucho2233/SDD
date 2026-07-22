import uuid

import pytest

pytestmark = pytest.mark.asyncio


async def _crear_reserva_activa(client, vehiculo_id, periodo_futuro_valido):
    inicio, fin = periodo_futuro_valido
    response = await client.post(
        "/reservas",
        json={
            "nombre_empleado": "Empleado Test",
            "legajo": "777",
            "licencia": "L-7",
            "vehiculo_id": str(vehiculo_id),
            "fecha_inicio": inicio.isoformat(),
            "fecha_fin": fin.isoformat(),
            "destino": "Depósito",
        },
    )
    assert response.status_code == 201


async def test_baja_temporal_es_200(client, admin_auth, vehiculo_activo):
    response = await client.post(
        f"/admin/vehiculos/{vehiculo_activo.id}/baja-temporal", auth=admin_auth
    )

    assert response.status_code == 200
    assert response.json()["estado"] == "baja_temporal"


async def test_baja_definitiva_es_200(client, admin_auth, vehiculo_activo):
    response = await client.post(
        f"/admin/vehiculos/{vehiculo_activo.id}/baja-definitiva", auth=admin_auth
    )

    assert response.status_code == 200
    assert response.json()["estado"] == "baja_definitiva"


async def test_baja_sin_credenciales_es_401(client, vehiculo_activo):
    response = await client.post(f"/admin/vehiculos/{vehiculo_activo.id}/baja-temporal")

    assert response.status_code == 401


async def test_baja_vehiculo_inexistente_es_404(client, admin_auth):
    response = await client.post(f"/admin/vehiculos/{uuid.uuid4()}/baja-temporal", auth=admin_auth)

    assert response.status_code == 404


async def test_baja_temporal_con_reservas_activas_es_409(
    client, admin_auth, vehiculo_activo, periodo_futuro_valido
):
    await _crear_reserva_activa(client, vehiculo_activo.id, periodo_futuro_valido)

    response = await client.post(
        f"/admin/vehiculos/{vehiculo_activo.id}/baja-temporal", auth=admin_auth
    )

    assert response.status_code == 409


async def test_baja_definitiva_con_reservas_activas_es_409(
    client, admin_auth, vehiculo_activo, periodo_futuro_valido
):
    await _crear_reserva_activa(client, vehiculo_activo.id, periodo_futuro_valido)

    response = await client.post(
        f"/admin/vehiculos/{vehiculo_activo.id}/baja-definitiva", auth=admin_auth
    )

    assert response.status_code == 409
