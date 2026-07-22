from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from app.services.reserva_service import es_activa, estado_derivado

AHORA = datetime(2026, 8, 1, 12, 0, tzinfo=timezone.utc)


@dataclass
class ReservaFalsa:
    fecha_inicio: datetime
    fecha_fin: datetime
    cancelada: bool = False


def test_reserva_futura():
    r = ReservaFalsa(AHORA + timedelta(hours=1), AHORA + timedelta(hours=2))
    assert estado_derivado(r, AHORA) == "futura"
    assert es_activa(r, AHORA) is True


def test_reserva_en_curso():
    r = ReservaFalsa(AHORA - timedelta(hours=1), AHORA + timedelta(hours=1))
    assert estado_derivado(r, AHORA) == "en_curso"
    assert es_activa(r, AHORA) is True


def test_reserva_pasada():
    r = ReservaFalsa(AHORA - timedelta(hours=3), AHORA - timedelta(hours=1))
    assert estado_derivado(r, AHORA) == "pasada"
    assert es_activa(r, AHORA) is False


def test_reserva_cancelada_no_es_activa_aunque_sea_futura():
    r = ReservaFalsa(AHORA + timedelta(hours=1), AHORA + timedelta(hours=2), cancelada=True)
    assert es_activa(r, AHORA) is False
