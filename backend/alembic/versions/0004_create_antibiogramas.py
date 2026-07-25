"""cria tabelas de antibiogramas

Revision ID: 0004_create_antibiogramas
Revises: 0003_create_microbiologia
Create Date: 2026-07-23

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0004_create_antibiogramas"
down_revision: Union[str, None] = "0003_create_microbiologia"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    resultado_sir_enum = postgresql.ENUM(
        "SENSIVEL", "INTERMEDIARIO", "RESISTENTE", name="resultado_sir_enum"
    )
    resultado_sir_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "antimicrobianos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("nome", sa.String(length=150), nullable=False),
        sa.Column("sigla", sa.String(length=20), nullable=True),
        sa.Column("classe", sa.String(length=100), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_unique_constraint("uq_antimicrobianos_nome", "antimicrobianos", ["nome"])
    op.create_index("ix_antimicrobianos_nome", "antimicrobianos", ["nome"])

    op.create_table(
        "antibiogramas",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column(
            "cultura_microrganismo_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("cultura_microrganismos.id"),
            nullable=False,
        ),
        sa.Column("data_liberacao", sa.DateTime(timezone=True), nullable=True),
        sa.Column("observacoes", sa.String(length=1000), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(
        "ix_antibiogramas_cultura_microrganismo_id",
        "antibiogramas",
        ["cultura_microrganismo_id"],
    )

    op.create_table(
        "antibiograma_resultados",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column(
            "antibiograma_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("antibiogramas.id"),
            nullable=False,
        ),
        sa.Column(
            "antimicrobiano_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("antimicrobianos.id"),
            nullable=False,
        ),
        sa.Column("resultado", resultado_sir_enum, nullable=False),
    )
    op.create_index(
        "ix_antibiograma_resultados_antibiograma_id",
        "antibiograma_resultados",
        ["antibiograma_id"],
    )
    op.create_index(
        "ix_antibiograma_resultados_antimicrobiano_id",
        "antibiograma_resultados",
        ["antimicrobiano_id"],
    )


def downgrade() -> None:
    op.drop_table("antibiograma_resultados")
    op.drop_index("ix_antibiogramas_cultura_microrganismo_id", table_name="antibiogramas")
    op.drop_table("antibiogramas")
    op.drop_index("ix_antimicrobianos_nome", table_name="antimicrobianos")
    op.drop_constraint("uq_antimicrobianos_nome", "antimicrobianos", type_="unique")
    op.drop_table("antimicrobianos")

    postgresql.ENUM(name="resultado_sir_enum").drop(op.get_bind(), checkfirst=True)
