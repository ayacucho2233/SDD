import uuid

import pytest

pytestmark = pytest.mark.asyncio


async def test_disponibilidad_vehiculo_libre(client, vehiculo_activo, periodo_futuro_valido):
    inicio, fin = periodo_futuro_valido

    response = await client.get(
        f"/vehiculos/{vehiculo_activo.id}/disponibilidad",
        params={"inicio": inicio.isoformat(), "fin": fin.isoformat()},
    )

    assert response.status_code == 200
    assert response.json() == {"disponible": True}


async def test_disponibilidad_fin_menor_igual_inicio_es_400(client, vehiculo_activo, periodo_futuro_valido):
    inicio, _ = periodo_futuro_valido

    response = await client.get(
        f"/vehiculos/{vehiculo_activo.id}/disponibilidad",
        params={"inicio": inicio.isoformat(), "fin": inicio.isoformat()},
    )

    assert response.status_code == 400


async def test_disponibilidad_vehiculo_inexistente_es_404(client, periodo_futuro_valido):
    inicio, fin = periodo_futuro_valido

    response = await client.get(
        f"/vehiculos/{uuid.uuid4()}/disponibilidad",
        params={"inicio": inicio.isoformat(), "fin": fin.isoformat()},
    )

    assert response.status_code == 404
