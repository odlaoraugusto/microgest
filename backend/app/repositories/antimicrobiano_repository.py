"""
Repository do catálogo de Antimicrobianos.
"""
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.antimicrobiano import Antimicrobiano
from app.repositories.base import BaseRepository


class AntimicrobianoRepository(BaseRepository[Antimicrobiano]):
    def __init__(self, db: Session):
        super().__init__(db, Antimicrobiano)

    def get_by_nome(self, nome: str) -> Antimicrobiano | None:
        stmt = select(Antimicrobiano).where(
            Antimicrobiano.nome.ilike(nome), Antimicrobiano.is_active.is_(True)
        )
        return self.db.scalars(stmt).first()

    def search(
        self, termo: str | None, skip: int = 0, limit: int = 20
    ) -> tuple[list[Antimicrobiano], int]:
        stmt = select(Antimicrobiano).where(Antimicrobiano.is_active.is_(True))

        if termo:
            like_termo = f"%{termo}%"
            stmt = stmt.where(
                or_(
                    Antimicrobiano.nome.ilike(like_termo),
                    Antimicrobiano.classe.ilike(like_termo),
                )
            )

        total = len(self.db.scalars(stmt).all())
        items = (
            self.db.scalars(stmt.offset(skip).limit(limit).order_by(Antimicrobiano.nome))
            .all()
        )
        return list(items), total
