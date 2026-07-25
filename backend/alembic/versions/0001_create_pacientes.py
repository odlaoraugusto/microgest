"""cria tabela pacientes

Revision ID: 0001_create_pacientes
Revises:
Create Date: 2026-07-23

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0001_create_pacientes"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    sexo_enum = postgresql.ENUM(
        "MASCULINO", "FEMININO", "NAO_INFORMADO", name="sexo_enum"
    )
    status_enum = postgresql.ENUM(
        "INTERNADO", "AMBULATORIAL", "ALTA", "OBITO", name="status_internacao_enum"
    )
    sexo_enum.create(op.get_bind(), checkfirst=True)
    status_enum.create(op.get_bind(), checkfirst=True)
    sexo_enum.create_type = False
    status_enum.create_type = False

    op.create_table(
        "pacientes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("nome", sa.String(length=200), nullable=False),
        sa.Column("prontuario", sa.String(length=50), nullable=False),
        sa.Column("data_nascimento", sa.Date(), nullable=True),
        sa.Column("sexo", sexo_enum, nullable=False, server_default="NAO_INFORMADO"),
        sa.Column("setor", sa.String(length=100), nullable=True),
        sa.Column("leito", sa.String(length=20), nullable=True),
        sa.Column(
            "status_internacao",
            status_enum,
            nullable=False,
            server_default="AMBULATORIAL",
        ),
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
    op.create_unique_constraint("uq_pacientes_prontuario", "pacientes", ["prontuario"])
    op.create_index("ix_pacientes_prontuario", "pacientes", ["prontuario"])


def downgrade() -> None:
    op.drop_index("ix_pacientes_prontuario", table_name="pacientes")
    op.drop_constraint("uq_pacientes_prontuario", "pacientes", type_="unique")
    op.drop_table("pacientes")
    postgresql.ENUM(name="status_internacao_enum").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="sexo_enum").drop(op.get_bind(), checkfirst=True)
