"""cria tabelas de microbiologia

Revision ID: 0003_create_microbiologia
Revises: 0002_create_solicitacoes
Create Date: 2026-07-23

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0003_create_microbiologia"
down_revision: Union[str, None] = "0002_create_solicitacoes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    gram_enum = postgresql.ENUM(
        "POSITIVO", "NEGATIVO", "NAO_SE_APLICA", name="gram_enum"
    )
    tipo_micro_enum = postgresql.ENUM(
        "BACTERIA", "FUNGO", "MICOBACTERIA", "VIRUS", "PARASITA", "OUTRO",
        name="tipo_microrganismo_enum",
    )
    resultado_enum = postgresql.ENUM(
        "EM_ANALISE", "POSITIVA", "NEGATIVA", "CONTAMINADA",
        name="resultado_cultura_enum",
    )
    gram_enum.create(op.get_bind(), checkfirst=True)
    tipo_micro_enum.create(op.get_bind(), checkfirst=True)
    resultado_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "microrganismos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("nome", sa.String(length=150), nullable=False),
        sa.Column("nome_cientifico", sa.String(length=150), nullable=True),
        sa.Column("gram", gram_enum, nullable=False, server_default="NAO_SE_APLICA"),
        sa.Column("tipo", tipo_micro_enum, nullable=False, server_default="BACTERIA"),
        sa.Column("familia", sa.String(length=100), nullable=True),
        sa.Column("relevancia_clinica", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_unique_constraint("uq_microrganismos_nome", "microrganismos", ["nome"])
    op.create_index("ix_microrganismos_nome", "microrganismos", ["nome"])

    op.create_table(
        "culturas",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column(
            "solicitacao_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("solicitacoes.id"),
            nullable=False,
        ),
        sa.Column("resultado", resultado_enum, nullable=False, server_default="EM_ANALISE"),
        sa.Column("liberado_tecnicamente", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("data_liberacao", sa.DateTime(timezone=True), nullable=True),
        sa.Column("observacoes", sa.String(length=1000), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_culturas_solicitacao_id", "culturas", ["solicitacao_id"])

    op.create_table(
        "cultura_microrganismos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column(
            "cultura_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("culturas.id"), nullable=False
        ),
        sa.Column(
            "microrganismo_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("microrganismos.id"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_cultura_microrganismos_cultura_id", "cultura_microrganismos", ["cultura_id"]
    )
    op.create_index(
        "ix_cultura_microrganismos_microrganismo_id",
        "cultura_microrganismos",
        ["microrganismo_id"],
    )


def downgrade() -> None:
    op.drop_table("cultura_microrganismos")
    op.drop_index("ix_culturas_solicitacao_id", table_name="culturas")
    op.drop_table("culturas")
    op.drop_index("ix_microrganismos_nome", table_name="microrganismos")
    op.drop_constraint("uq_microrganismos_nome", "microrganismos", type_="unique")
    op.drop_table("microrganismos")

    postgresql.ENUM(name="resultado_cultura_enum").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="tipo_microrganismo_enum").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="gram_enum").drop(op.get_bind(), checkfirst=True)
