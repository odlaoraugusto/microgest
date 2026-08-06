"""adiciona sem_antibiograma_padronizado em cultura_microrganismos

Revision ID: 0011_add_sem_antibiograma
Revises: 0010_add_grupo_cultura
Create Date: 2026-08-06

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
# OBS: mantenha o revision id com no máximo 32 caracteres - é o tamanho da
# coluna alembic_version.version_num criada pela migration inicial (ver
# 0001_create_pacientes.py), e um ID mais longo quebra o "alembic upgrade".
revision: str = "0011_add_sem_antibiograma"
down_revision: Union[str, None] = "0010_add_grupo_cultura"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "cultura_microrganismos",
        sa.Column(
            "sem_antibiograma_padronizado",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
    )


def downgrade() -> None:
    op.drop_column("cultura_microrganismos", "sem_antibiograma_padronizado")
