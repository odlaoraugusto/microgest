"""
Repository do catálogo de Setores.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.setor import Setor
from app.repositories.base import BaseRepository


class SetorRepository(BaseRepository[Setor]):
    def __init__(self, db: Session):
        super().__init__(db, Setor)

    def get_by_nome(self, nome: str) -> Setor | None:
        stmt = select(Setor).where(Setor.nome.ilike(nome), Setor.is_active.is_(True))
        return self.db.scalars(stmt).first()

    def listar_todos(self) -> list[Setor]:
        stmt = select(Setor).where(Setor.is_active.is_(True)).order_by(Setor.nome)
        return list(self.db.scalars(stmt).all())
