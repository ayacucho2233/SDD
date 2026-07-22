"""initial schema: vehiculos y reservas

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-22

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "vehiculos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("patente", sa.String(length=10), nullable=False),
        sa.Column("tipo", sa.String(length=10), nullable=False),
        sa.Column("estado", sa.String(length=20), nullable=False, server_default="activo"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint("tipo IN ('auto','camioneta')", name="ck_vehiculo_tipo"),
        sa.CheckConstraint(
            "estado IN ('activo','baja_temporal','baja_definitiva')",
            name="ck_vehiculo_estado",
        ),
    )
    op.create_index("ix_vehiculos_patente", "vehiculos", ["patente"], unique=True)

    op.create_table(
        "reservas",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "vehiculo_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("vehiculos.id"),
            nullable=False,
        ),
        sa.Column("nombre_empleado", sa.String(length=200), nullable=False),
        sa.Column("legajo", sa.String(length=20), nullable=False),
        sa.Column("licencia", sa.String(length=20), nullable=False),
        sa.Column("fecha_inicio", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fecha_fin", sa.DateTime(timezone=True), nullable=False),
        sa.Column("destino", sa.String(length=300), nullable=False),
        sa.Column("cancelada", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint("fecha_fin > fecha_inicio", name="ck_reserva_periodo_valido"),
    )
    op.create_index(
        "ix_reserva_vehiculo_periodo",
        "reservas",
        ["vehiculo_id", "fecha_inicio", "fecha_fin"],
    )
    op.create_index("ix_reservas_legajo", "reservas", ["legajo"])


def downgrade() -> None:
    op.drop_index("ix_reservas_legajo", table_name="reservas")
    op.drop_index("ix_reserva_vehiculo_periodo", table_name="reservas")
    op.drop_table("reservas")
    op.drop_index("ix_vehiculos_patente", table_name="vehiculos")
    op.drop_table("vehiculos")
