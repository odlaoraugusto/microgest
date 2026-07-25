"""cria tabela usuarios

Revision ID: 0005_create_usuarios
Revises: 0004_create_antibiogramas
Create Date: 2026-07-23

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0005_create_usuarios"
down_revision: Union[str, None] = "0004_create_antibiogramas"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    perfil_enum = postgresql.ENUM(
        "ADMIN", "BIOMEDICO", "TECNICO", "VISUALIZADOR", name="perfil_usuario_enum"
    )
    perfil_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "usuarios",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("nome", sa.String(length=200), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("senha_hash", sa.String(length=255), nullable=False),
        sa.Column("perfil", perfil_enum, nullable=False, server_default="VISUALIZADOR"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_unique_constraint("uq_usuarios_email", "usuarios", ["email"])
    op.create_index("ix_usuarios_email", "usuarios", ["email"])


def downgrade() -> None:
    op.drop_index("ix_usuarios_email", table_name="usuarios")
    op.drop_constraint("uq_usuarios_email", "usuarios", type_="unique")
    op.drop_table("usuarios")
    postgresql.ENUM(name="perfil_usuario_enum").drop(op.get_bind(), checkfirst=True)
