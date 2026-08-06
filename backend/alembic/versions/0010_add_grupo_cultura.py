"""adiciona grupo (classificacao) as culturas

Revision ID: 0010_add_grupo_cultura
Revises: 0009_create_setores_materiais
Create Date: 2026-07-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0010_add_grupo_cultura"
down_revision: Union[str, None] = "0009_create_setores_materiais"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

GRUPO_CULTURA_ENUM = sa.Enum(
    "HEMOCULTURA",
    "CULTURA_GERAL",
    "VIGILANCIA",
    "BK",
    "FUNGOS",
    name="grupo_cultura_enum",
)


def upgrade() -> None:
    GRUPO_CULTURA_ENUM.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "culturas",
        sa.Column(
            "grupo",
            GRUPO_CULTURA_ENUM,
            nullable=False,
            server_default="CULTURA_GERAL",
        ),
    )
    op.create_index("ix_culturas_grupo", "culturas", ["grupo"])


def downgrade() -> None:
    op.drop_index("ix_culturas_grupo", table_name="culturas")
    op.drop_column("culturas", "grupo")
    GRUPO_CULTURA_ENUM.drop(op.get_bind(), checkfirst=True)
