import pytest

pytestmark = pytest.mark.asyncio


async def test_lista_vehiculos_incluye_patente_y_tipo(client, vehiculo_activo):
    response = await client.get("/vehiculos")

    assert response.status_code == 200
    body = response.json()
    assert any(
        v["patente"] == vehiculo_activo.patente and v["tipo"] == vehiculo_activo.tipo
        for v in body
    )


async def test_lista_vehiculos_con_filtro_disponibilidad(client, vehiculo_activo, periodo_futuro_valido):
    inicio, fin = periodo_futuro_valido

    response = await client.get(
        "/vehiculos",
        params={
            "disponible_desde": inicio.isoformat(),
            "disponible_hasta": fin.isoformat(),
        },
    )

    assert response.status_code == 200
    body = response.json()
    vehiculo = next(v for v in body if v["patente"] == vehiculo_activo.patente)
    assert vehiculo["disponible"] is True


async def test_lista_vehiculos_filtro_incompleto_es_400(client, vehiculo_activo, periodo_futuro_valido):
    inicio, _ = periodo_futuro_valido

    response = await client.get("/vehiculos", params={"disponible_desde": inicio.isoformat()})

    assert response.status_code == 400
