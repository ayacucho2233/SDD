import asyncio
import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import get_settings  # noqa: E402
from app.database import Base  # noqa: E402
from app.models import reserva, vehiculo  # noqa: E402,F401 (registran los modelos en Base.metadata)

config = context.config

# Reusar app.config.get_settings() (en vez de os.environ.get("DATABASE_URL"))
# para que alembic lea DATABASE_URL desde backend/.env igual que la propia
# app — os.environ.get() por sí solo NO carga el archivo .env.
config.set_main_option("sqlalchemy.url", get_settings().database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    # No usar async_engine_from_config(config.get_section(...)): la sección
    # [alembic] del .ini no trae "sqlalchemy.url" a propósito (nunca
    # hardcodear credenciales, ver Agents.md), y set_main_option() no
    # garantiza reflejarse en get_section() en todas las versiones de
    # Alembic. Se arma el engine directo con la URL ya resuelta.
    connectable = create_async_engine(
        config.get_main_option("sqlalchemy.url"), poolclass=NullPool
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
