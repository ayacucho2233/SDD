import pytest

from app.services.exceptions import ConflictoError, SolicitudInvalidaError
from app.services.vehiculo_service import validar_baja, validar_reactivacion


def test_validar_baja_permite_desde_activo_sin_reservas():
    validar_baja(estado_actual="activo", tiene_reservas_activas=False)  # no debe lanzar


def test_validar_baja_permite_definitiva_desde_baja_temporal():
    validar_baja(estado_actual="baja_temporal", tiene_reservas_activas=False)  # no debe lanzar


def test_validar_baja_bloqueada_si_tiene_reservas_activas():
    with pytest.raises(ConflictoError):
        validar_baja(estado_actual="activo", tiene_reservas_activas=True)


def test_validar_reactivacion_permite_desde_baja_temporal():
    validar_reactivacion(estado_actual="baja_temporal")  # no debe lanzar


def test_validar_reactivacion_bloqueada_desde_baja_definitiva():
    with pytest.raises(ConflictoError):
        validar_reactivacion(estado_actual="baja_definitiva")


def test_validar_reactivacion_bloqueada_si_ya_esta_activo():
    with pytest.raises(ConflictoError):
        validar_reactivacion(estado_actual="activo")
