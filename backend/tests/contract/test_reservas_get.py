from datetime import timedelta

import pytest

pytestmark = pytest.mark.asyncio


async def _crear_reserva(client, vehiculo_id, inicio, fin, legajo="999"):
    payload = {
        "nombre_empleado": "Empleado Test",
        "legajo": legajo,
        "licencia": "L-0",
        "vehiculo_id": str(vehiculo_id),
        "fecha_inicio": inicio.isoformat(),
        "fecha_fin": fin.isoformat(),
        "destino": "Sucursal Centro",
    }
    response = await client.post("/reservas", json=payload)
    assert response.status_code == 201
    return response.json()


async def test_listar_reservas_sin_filtro_devuelve_todas(client, vehiculo_activo, periodo_futuro_valido):
    inicio, fin = periodo_futuro_valido
    await _crear_reserva(client, vehiculo_activo.id, inicio, fin)

    response = await client.get("/reservas")

    assert response.status_code == 200
    assert len(response.json()) >= 1


async def test_listar_reservas_filtro_futuras(client, vehiculo_activo, periodo_futuro_valido):
    inicio, fin = periodo_futuro_valido
    creada = await _crear_reserva(client, vehiculo_activo.id, inicio, fin)

    response = await client.get("/reservas", params={"estado": "futura"})

    assert response.status_code == 200
    ids = [r["id"] for r in response.json()]
    assert creada["id"] in ids
    assert all(r["estado"] == "futura" for r in response.json())


async def test_listar_reservas_filtro_pasadas_no_incluye_futuras(
    client, vehiculo_activo, periodo_futuro_valido
):
    inicio, fin = periodo_futuro_valido
    await _crear_reserva(client, vehiculo_activo.id, inicio, fin)

    response = await client.get("/reservas", params={"estado": "pasada"})

    assert response.status_code == 200
    assert response.json() == []
