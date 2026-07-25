"""
Repository do catálogo de Materiais.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.material import Material
from app.repositories.base import BaseRepository


class MaterialRepository(BaseRepository[Material]):
    def __init__(self, db: Session):
        super().__init__(db, Material)

    def get_by_nome(self, nome: str) -> Material | None:
        stmt = select(Material).where(Material.nome.ilike(nome), Material.is_active.is_(True))
        return self.db.scalars(stmt).first()

    def listar_todos(self) -> list[Material]:
        stmt = select(Material).where(Material.is_active.is_(True)).order_by(Material.nome)
        return list(self.db.scalars(stmt).all())
