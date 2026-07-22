import asyncio

import pytest

pytestmark = pytest.mark.asyncio


async def test_dos_reservas_simultaneas_solo_una_se_confirma(
    client, vehiculo_activo, periodo_futuro_valido
):
    """SC-003 / AC-06: ante dos solicitudes concurrentes para el mismo vehículo
    y período, exactamente una debe confirmarse (201) y la otra rechazarse (409)."""
    inicio, fin = periodo_futuro_valido
    payload = {
        "nombre_empleado": "Empleado Uno",
        "legajo": "111",
        "licencia": "L-1",
        "vehiculo_id": str(vehiculo_activo.id),
        "fecha_inicio": inicio.isoformat(),
        "fecha_fin": fin.isoformat(),
        "destino": "Depósito",
    }
    payload_b = {**payload, "nombre_empleado": "Empleado Dos", "legajo": "222", "licencia": "L-2"}

    resultados = await asyncio.gather(
        client.post("/reservas", json=payload),
        client.post("/reservas", json=payload_b),
    )

    status_codes = sorted(r.status_code for r in resultados)
    assert status_codes == [201, 409]
