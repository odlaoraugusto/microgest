"""
Repository do módulo Pacientes.

Além do CRUD genérico (herdado de BaseRepository), implementa a busca
por prontuário e por nome, usadas pelo módulo de Pacientes (Documento
Mestre, seção 6).
"""
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.paciente import Paciente
from app.repositories.base import BaseRepository


class PacienteRepository(BaseRepository[Paciente]):
    def __init__(self, db: Session):
        super().__init__(db, Paciente)

    def get_by_prontuario(self, prontuario: str) -> Paciente | None:
        stmt = select(Paciente).where(
            Paciente.prontuario == prontuario, Paciente.is_active.is_(True)
        )
        return self.db.scalars(stmt).first()

    def search(
        self, termo: str | None, skip: int = 0, limit: int = 20
    ) -> tuple[list[Paciente], int]:
        stmt = select(Paciente).where(Paciente.is_active.is_(True))

        if termo:
            like_termo = f"%{termo}%"
            stmt = stmt.where(
                or_(
                    Paciente.nome.ilike(like_termo),
                    Paciente.prontuario.ilike(like_termo),
                )
            )

        total = len(self.db.scalars(stmt).all())
        items = (
            self.db.scalars(
                stmt.offset(skip).limit(limit).order_by(Paciente.created_at.desc())
            )
            .all()
        )
        return list(items), total
