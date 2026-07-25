"""cria tabela parametros_sistema

Revision ID: 0006_create_parametros_sistema
Revises: 0005_create_usuarios
Create Date: 2026-07-23

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0006_create_parametros_sistema"
down_revision: Union[str, None] = "0005_create_usuarios"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


parametros_table = sa.table(
    "parametros_sistema",
    sa.column("id", postgresql.UUID(as_uuid=True)),
    sa.column("chave", sa.String),
    sa.column("valor", sa.String),
    sa.column("descricao", sa.String),
)


def upgrade() -> None:
    op.create_table(
        "parametros_sistema",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("chave", sa.String(length=100), nullable=False),
        sa.Column("valor", sa.String(length=500), nullable=False),
        sa.Column("descricao", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_unique_constraint(
        "uq_parametros_sistema_chave", "parametros_sistema", ["chave"]
    )
    op.create_index("ix_parametros_sistema_chave", "parametros_sistema", ["chave"])

    op.bulk_insert(
        parametros_table,
        [
            {
                "id": uuid.uuid4(),
                "chave": "prazo_solicitacao_dias",
                "valor": "2",
                "descricao": (
                    "Número de dias após a solicitação para considerá-la com "
                    "prazo vencido, caso ainda não tenha sido liberada."
                ),
            }
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_parametros_sistema_chave", table_name="parametros_sistema")
    op.drop_constraint("uq_parametros_sistema_chave", "parametros_sistema", type_="unique")
    op.drop_table("parametros_sistema")
