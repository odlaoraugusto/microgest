"""cria tabela logs_auditoria

Revision ID: 0007_create_logs_auditoria
Revises: 0006_create_parametros_sistema
Create Date: 2026-07-23

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0007_create_logs_auditoria"
down_revision: Union[str, None] = "0006_create_parametros_sistema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "logs_auditoria",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("usuario_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("usuario_email", sa.String(length=255), nullable=True),
        sa.Column("metodo", sa.String(length=10), nullable=False),
        sa.Column("caminho", sa.String(length=300), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=False),
        sa.Column("ip_origem", sa.String(length=64), nullable=True),
        sa.Column(
            "criado_em", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_logs_auditoria_usuario_id", "logs_auditoria", ["usuario_id"])
    op.create_index("ix_logs_auditoria_criado_em", "logs_auditoria", ["criado_em"])


def downgrade() -> None:
    op.drop_index("ix_logs_auditoria_criado_em", table_name="logs_auditoria")
    op.drop_index("ix_logs_auditoria_usuario_id", table_name="logs_auditoria")
    op.drop_table("logs_auditoria")
