from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from app.services.disponibilidad_service import hay_solapamiento


@dataclass
class ReservaFalsa:
    fecha_inicio: datetime
    fecha_fin: datetime


def _rango(offset_horas_inicio: int, offset_horas_fin: int) -> tuple[datetime, datetime]:
    base = datetime(2026, 8, 1, tzinfo=timezone.utc)
    return base + timedelta(hours=offset_horas_inicio), base + timedelta(hours=offset_horas_fin)


def test_sin_reservas_existentes_no_hay_solapamiento():
    inicio, fin = _rango(0, 2)
    assert hay_solapamiento([], inicio, fin) is False


def test_periodos_identicos_solapan():
    inicio, fin = _rango(0, 2)
    existente = ReservaFalsa(fecha_inicio=inicio, fecha_fin=fin)
    assert hay_solapamiento([existente], inicio, fin) is True


def test_periodo_nuevo_empieza_durante_el_existente_solapa():
    existente = ReservaFalsa(*_rango(0, 4))
    nuevo_inicio, nuevo_fin = _rango(2, 6)
    assert hay_solapamiento([existente], nuevo_inicio, nuevo_fin) is True


def test_periodo_nuevo_contiene_al_existente_solapa():
    existente = ReservaFalsa(*_rango(2, 3))
    nuevo_inicio, nuevo_fin = _rango(0, 5)
    assert hay_solapamiento([existente], nuevo_inicio, nuevo_fin) is True


def test_periodos_consecutivos_sin_solapar_no_solapan():
    existente = ReservaFalsa(*_rango(0, 2))
    nuevo_inicio, nuevo_fin = _rango(2, 4)
    assert hay_solapamiento([existente], nuevo_inicio, nuevo_fin) is False


def test_periodos_totalmente_separados_no_solapan():
    existente = ReservaFalsa(*_rango(0, 1))
    nuevo_inicio, nuevo_fin = _rango(5, 6)
    assert hay_solapamiento([existente], nuevo_inicio, nuevo_fin) is False
