"""
Repository do módulo Antibiogramas.
"""
import uuid

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, joinedload

from app.models.antibiograma import Antibiograma, AntibiogramaResultado
from app.models.cultura import CulturaMicrorganismo
from app.repositories.base import BaseRepository


class AntibiogramaRepository(BaseRepository[Antibiograma]):
    def __init__(self, db: Session):
        super().__init__(db, Antibiograma)

    def _base_query(self):
        return select(Antibiograma).options(
            joinedload(Antibiograma.cultura_microrganismo).joinedload(
                CulturaMicrorganismo.microrganismo
            ),
            joinedload(Antibiograma.resultados).joinedload(
                AntibiogramaResultado.antimicrobiano
            ),
        )

    def get_by_id(self, entity_id: uuid.UUID) -> Antibiograma | None:
        stmt = self._base_query().where(Antibiograma.id == entity_id)
        return self.db.scalars(stmt).unique().first()

    def search(
        self,
        cultura_microrganismo_id: uuid.UUID | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Antibiograma], int]:
        stmt = self._base_query().where(Antibiograma.is_active.is_(True))

        if cultura_microrganismo_id:
            stmt = stmt.where(
                Antibiograma.cultura_microrganismo_id == cultura_microrganismo_id
            )

        total = len(self.db.scalars(stmt).unique().all())
        items = (
            self.db.scalars(
                stmt.offset(skip).limit(limit).order_by(Antibiograma.created_at.desc())
            )
            .unique()
            .all()
        )
        return list(items), total

    def definir_resultados(self, antibiograma_id: uuid.UUID, resultados: list[dict]):
        """Substitui a lista de resultados S/I/R do antibiograma."""
        self.db.execute(
            delete(AntibiogramaResultado).where(
                AntibiogramaResultado.antibiograma_id == antibiograma_id
            )
        )
        for item in resultados:
            self.db.add(
                AntibiogramaResultado(
                    antibiograma_id=antibiograma_id,
                    antimicrobiano_id=item["antimicrobiano_id"],
                    resultado=item["resultado"],
                )
            )
        self.db.commit()
