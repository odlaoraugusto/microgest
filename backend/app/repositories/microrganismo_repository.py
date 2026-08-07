"""
Repository do catálogo de Microrganismos.
"""
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.microrganismo import Microrganismo
from app.repositories.base import BaseRepository


class MicrorganismoRepository(BaseRepository[Microrganismo]):
    def __init__(self, db: Session):
        super().__init__(db, Microrganismo)

    def get_by_nome(self, nome: str) -> Microrganismo | None:
        stmt = select(Microrganismo).where(
            Microrganismo.nome.ilike(nome), Microrganismo.is_active.is_(True)
        )
        return self.db.scalars(stmt).first()

    def get_by_genero(self, genero: str) -> Microrganismo | None:
        """Primeiro microrganismo ativo cujo nome comece pelo gênero informado
        (ex.: "Klebsiella" casa com "Klebsiella pneumoniae"). Usado pela
        herança automática de taxonomia ao cadastrar uma espécie nova de um
        gênero já conhecido - ver MicrorganismoService.criar."""
        stmt = (
            select(Microrganismo)
            .where(
                Microrganismo.nome.ilike(f"{genero} %"),
                Microrganismo.is_active.is_(True),
            )
            .order_by(Microrganismo.nome)
        )
        return self.db.scalars(stmt).first()

    def search(
        self, termo: str | None, skip: int = 0, limit: int = 20
    ) -> tuple[list[Microrganismo], int]:
        stmt = select(Microrganismo).where(Microrganismo.is_active.is_(True))

        if termo:
            like_termo = f"%{termo}%"
            stmt = stmt.where(
                or_(
                    Microrganismo.nome.ilike(like_termo),
                    Microrganismo.familia.ilike(like_termo),
                )
            )

        total = len(self.db.scalars(stmt).all())
        items = (
            self.db.scalars(stmt.offset(skip).limit(limit).order_by(Microrganismo.nome))
            .all()
        )
        return list(items), total
