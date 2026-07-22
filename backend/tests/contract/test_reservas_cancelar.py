import uuid

import pytest

pytestmark = pytest.mark.asyncio


async def _crear_reserva(client, vehiculo_id, inicio, fin, legajo="555"):
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


async def test_cancelar_reserva_propia_es_200(client, vehiculo_activo, periodo_futuro_valido):
    inicio, fin = periodo_futuro_valido
    reserva = await _crear_reserva(client, vehiculo_activo.id, inicio, fin, legajo="555")

    response = await client.post(f"/reservas/{reserva['id']}/cancelar", json={"legajo": "555"})

    assert response.status_code == 200
    assert response.json()["cancelada"] is True


async def test_cancelar_con_legajo_distinto_es_403(client, vehiculo_activo, periodo_futuro_valido):
    inicio, fin = periodo_futuro_valido
    reserva = await _crear_reserva(client, vehiculo_activo.id, inicio, fin, legajo="555")

    response = await client.post(f"/reservas/{reserva['id']}/cancelar", json={"legajo": "otro-legajo"})

    assert response.status_code == 403


async def test_cancelar_reserva_ya_cancelada_es_409(client, vehiculo_activo, periodo_futuro_valido):
    inicio, fin = periodo_futuro_valido
    reserva = await _crear_reserva(client, vehiculo_activo.id, inicio, fin, legajo="555")
    await client.post(f"/reservas/{reserva['id']}/cancelar", json={"legajo": "555"})

    response = await client.post(f"/reservas/{reserva['id']}/cancelar", json={"legajo": "555"})

    assert response.status_code == 409


async def test_cancelar_reserva_inexistente_es_404(client):
    response = await client.post(f"/reservas/{uuid.uuid4()}/cancelar", json={"legajo": "555"})

    assert response.status_code == 404
