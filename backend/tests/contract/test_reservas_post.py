import uuid
from datetime import timedelta

import pytest

pytestmark = pytest.mark.asyncio


def _payload(vehiculo_id, inicio, fin, **overrides):
    payload = {
        "nombre_empleado": "Ana Pérez",
        "legajo": "12345",
        "licencia": "L-9876",
        "vehiculo_id": str(vehiculo_id),
        "fecha_inicio": inicio.isoformat(),
        "fecha_fin": fin.isoformat(),
        "destino": "Planta Norte",
    }
    payload.update(overrides)
    return payload


async def test_crear_reserva_exitosa_es_201(client, vehiculo_activo, periodo_futuro_valido):
    inicio, fin = periodo_futuro_valido

    response = await client.post("/reservas", json=_payload(vehiculo_activo.id, inicio, fin))

    assert response.status_code == 201
    body = response.json()
    assert body["vehiculo_id"] == str(vehiculo_activo.id)
    assert body["cancelada"] is False


async def test_crear_reserva_sin_destino_es_400(client, vehiculo_activo, periodo_futuro_valido):
    inicio, fin = periodo_futuro_valido
    payload = _payload(vehiculo_activo.id, inicio, fin)
    del payload["destino"]

    response = await client.post("/reservas", json=payload)

    assert response.status_code in (400, 422)


async def test_crear_reserva_fecha_fin_igual_inicio_es_400(client, vehiculo_activo, periodo_futuro_valido):
    inicio, _ = periodo_futuro_valido

    response = await client.post("/reservas", json=_payload(vehiculo_activo.id, inicio, inicio))

    assert response.status_code == 400


async def test_crear_reserva_inicio_en_pasado_es_400(client, vehiculo_activo, periodo_futuro_valido):
    inicio, fin = periodo_futuro_valido
    inicio_pasado = inicio - timedelta(days=10)
    fin_pasado = inicio_pasado + timedelta(hours=2)

    response = await client.post(
        "/reservas", json=_payload(vehiculo_activo.id, inicio_pasado, fin_pasado)
    )

    assert response.status_code == 400


async def test_crear_reserva_vehiculo_inexistente_es_404(client, periodo_futuro_valido):
    inicio, fin = periodo_futuro_valido

    response = await client.post("/reservas", json=_payload(uuid.uuid4(), inicio, fin))

    assert response.status_code == 404


async def test_crear_reserva_con_solapamiento_es_409(client, vehiculo_activo, periodo_futuro_valido):
    inicio, fin = periodo_futuro_valido
    await client.post("/reservas", json=_payload(vehiculo_activo.id, inicio, fin))

    solapada_inicio = inicio + timedelta(hours=1)
    solapada_fin = fin + timedelta(hours=1)
    response = await client.post(
        "/reservas", json=_payload(vehiculo_activo.id, solapada_inicio, solapada_fin)
    )

    assert response.status_code == 409
