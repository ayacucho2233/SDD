import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext

from app.config import Settings, get_settings

security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def require_admin(
    credentials: HTTPBasicCredentials = Depends(security),
    settings: Settings = Depends(get_settings),
) -> str:
    """Dependencia FastAPI que exige HTTP Basic válido (FR-017)."""
    usuario_valido = secrets.compare_digest(credentials.username, settings.admin_user)
    # Siempre se verifica el hash (aunque el usuario no coincida) para no filtrar
    # por timing si el usuario ingresado existe o no.
    password_valida = pwd_context.verify(credentials.password, settings.admin_password_hash)

    if not (usuario_valido and password_valida):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales de administrador inválidas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
