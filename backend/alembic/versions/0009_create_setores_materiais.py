"""cria tabelas setores e materiais

Revision ID: 0009_create_setores_materiais
Revises: 0008_add_previsao_liberacao
Create Date: 2026-07-25

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0009_create_setores_materiais"
down_revision: Union[str, None] = "0008_add_previsao_liberacao"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _criar_tabela_catalogo(nome_tabela: str) -> None:
    op.create_table(
        nome_tabela,
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("nome", sa.String(length=100), nullable=False),
        sa.Column("descricao", sa.String(length=300), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_unique_constraint(f"uq_{nome_tabela}_nome", nome_tabela, ["nome"])
    op.create_index(f"ix_{nome_tabela}_nome", nome_tabela, ["nome"])


def upgrade() -> None:
    _criar_tabela_catalogo("setores")
    _criar_tabela_catalogo("materiais")

    # Semente inicial - valores comuns já usados nas conversas de
    # planejamento do projeto, para o catálogo não começar vazio.
    setores = sa.table(
        "setores", sa.column("id", postgresql.UUID(as_uuid=True)), sa.column("nome", sa.String)
    )
    materiais = sa.table(
        "materiais", sa.column("id", postgresql.UUID(as_uuid=True)), sa.column("nome", sa.String)
    )
    op.bulk_insert(
        setores,
        [
            {"id": uuid.uuid4(), "nome": nome}
            for nome in ["UTI", "UTIN", "Enfermaria", "Ambulatório", "Pronto-Socorro", "Centro Cirúrgico"]
        ],
    )
    op.bulk_insert(
        materiais,
        [
            {"id": uuid.uuid4(), "nome": nome}
            for nome in ["Hemocultura", "Urina", "Escarro", "Líquor", "Fezes", "Secreção Traqueal", "Ferida"]
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_materiais_nome", table_name="materiais")
    op.drop_constraint("uq_materiais_nome", "materiais", type_="unique")
    op.drop_table("materiais")
    op.drop_index("ix_setores_nome", table_name="setores")
    op.drop_constraint("uq_setores_nome", "setores", type_="unique")
    op.drop_table("setores")
