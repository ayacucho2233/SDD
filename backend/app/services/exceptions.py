class DominioError(Exception):
    """Excepción base para errores de reglas de negocio, traducidos a HTTP en los routers."""


class SolicitudInvalidaError(DominioError):
    """Mapea a 400."""


class NoAutorizadoError(DominioError):
    """Mapea a 403."""


class RecursoNoEncontradoError(DominioError):
    """Mapea a 404."""


class ConflictoError(DominioError):
    """Mapea a 409."""
