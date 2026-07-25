"""adiciona previsao_liberacao em culturas

Revision ID: 0008_add_previsao_liberacao
Revises: 0007_create_logs_auditoria
Create Date: 2026-07-24

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0008_add_previsao_liberacao"
down_revision: Union[str, None] = "0007_create_logs_auditoria"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("culturas", sa.Column("previsao_liberacao", sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column("culturas", "previsao_liberacao")
