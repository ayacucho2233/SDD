import os
import uuid
from collections.abc import AsyncIterator
from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

os.environ.setdefault(
    "DATABASE_URL",
    os.environ.get(
        "TEST_DATABASE_URL",
        "postgresql+asyncpg://reserva_app:reserva_app@localhost:5432/reserva_vehiculos_test",
    ),
)
os.environ.setdefault("ADMIN_USER", "admin")
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ADMIN_PASSWORD = "admin-test-password"
os.environ.setdefault("ADMIN_PASSWORD_HASH", _pwd_context.hash(ADMIN_PASSWORD))
os.environ.setdefault("APP_TIMEZONE", "America/Argentina/Buenos_Aires")
os.environ.setdefault("FRONTEND_ORIGIN", "http://localhost:5173")

from app.database import Base, get_session  # noqa: E402
from app.main import app  # noqa: E402
from app.models.vehiculo import Vehiculo  # noqa: E402

# NullPool: pytest-asyncio usa un event loop nuevo por test (function-scoped);
# un pool con conexiones reutilizables terminaría con conexiones "attached to
# a different loop" entre tests. Sin pooling, cada operación abre su propia
# conexión bajo el loop del test que la ejecuta.
test_engine = create_async_engine(os.environ["DATABASE_URL"], poolclass=NullPool)
TestSessionLocal = async_sessionmaker(bind=test_engine, expire_on_commit=False)


@pytest_asyncio.fixture(scope="session")
async def _prepare_schema():
    """Solo se ejecuta (y solo entonces requiere una base de datos real) para
    los tests que dependen de `db_session`/`client` — los tests unitarios en
    tests/unit/ no la solicitan y corren sin base de datos."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await test_engine.dispose()


@pytest_asyncio.fixture
async def db_session(_prepare_schema) -> AsyncIterator[AsyncSession]:
    async with TestSessionLocal() as session:
        yield session
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())
        await session.commit()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncIterator[AsyncClient]:
    # Cada request abre su propia sesión (igual que en producción), lo que
    # permite ejercitar `SELECT ... FOR UPDATE` con concurrencia real entre
    # requests simultáneos (ver tests/integration/test_concurrencia_reservas.py).
    async def _override_get_session() -> AsyncIterator[AsyncSession]:
        async with TestSessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = _override_get_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
def admin_auth() -> tuple[str, str]:
    return (os.environ["ADMIN_USER"], ADMIN_PASSWORD)


@pytest_asyncio.fixture
async def vehiculo_activo(db_session: AsyncSession) -> Vehiculo:
    vehiculo = Vehiculo(id=uuid.uuid4(), patente="AB123CD", tipo="auto", estado="activo")
    db_session.add(vehiculo)
    await db_session.commit()
    await db_session.refresh(vehiculo)
    return vehiculo


@pytest.fixture
def periodo_futuro_valido() -> tuple[datetime, datetime]:
    inicio = datetime.now(timezone.utc) + timedelta(days=1)
    fin = inicio + timedelta(hours=4)
    return inicio, fin
