"""cria tabela solicitacoes

Revision ID: 0002_create_solicitacoes
Revises: 0001_create_pacientes
Create Date: 2026-07-23

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0002_create_solicitacoes"
down_revision: Union[str, None] = "0001_create_pacientes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    prioridade_enum = postgresql.ENUM(
        "ROTINA", "URGENTE", "EMERGENCIA", name="prioridade_enum"
    )
    status_enum = postgresql.ENUM(
        "AGUARDANDO_COLETA",
        "COLETADO",
        "EM_ANALISE",
        "LIBERADO",
        "CANCELADO",
        name="status_solicitacao_enum",
    )
    prioridade_enum.create(op.get_bind(), checkfirst=True)
    status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "solicitacoes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column(
            "paciente_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("pacientes.id"),
            nullable=False,
        ),
        sa.Column("material", sa.String(length=100), nullable=False),
        sa.Column("origem", sa.String(length=100), nullable=True),
        sa.Column("prioridade", prioridade_enum, nullable=False, server_default="ROTINA"),
        sa.Column(
            "status", status_enum, nullable=False, server_default="AGUARDANDO_COLETA"
        ),
        sa.Column("data_solicitacao", sa.Date(), nullable=False),
        sa.Column("data_coleta", sa.DateTime(timezone=True), nullable=True),
        sa.Column("observacoes", sa.String(length=1000), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
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
    )
    op.create_index("ix_solicitacoes_paciente_id", "solicitacoes", ["paciente_id"])


def downgrade() -> None:
    op.drop_index("ix_solicitacoes_paciente_id", table_name="solicitacoes")
    op.drop_table("solicitacoes")
    postgresql.ENUM(name="status_solicitacao_enum").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="prioridade_enum").drop(op.get_bind(), checkfirst=True)
