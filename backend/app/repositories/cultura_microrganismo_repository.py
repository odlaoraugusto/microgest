"""
Repository auxiliar de consulta a isolados (CulturaMicrorganismo).

Usado pelo módulo Antibiogramas para validar se o isolado informado
existe e pertence a uma cultura com resultado POSITIVA.
"""
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.cultura import Cultura, CulturaMicrorganismo


class CulturaMicrorganismoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, entity_id: uuid.UUID) -> CulturaMicrorganismo | None:
        stmt = (
            select(CulturaMicrorganismo)
            .options(
                joinedload(CulturaMicrorganismo.microrganismo),
                joinedload(CulturaMicrorganismo.cultura),
            )
            .where(CulturaMicrorganismo.id == entity_id)
        )
        return self.db.scalars(stmt).first()

    def marcar_sem_antibiograma(
        self, isolado_id: uuid.UUID, valor: bool
    ) -> CulturaMicrorganismo | None:
        """
        Liga/desliga a flag de "sem antibiograma padronizado (BrCAST)" de um
        isolado - usada quando o microrganismo identificado não tem
        protocolo BrCAST definido, dispensando aquele isolado específico da
        exigência de antibiograma completo na liberação da cultura.
        """
        isolado = self.get_by_id(isolado_id)
        if not isolado:
            return None
        isolado.sem_antibiograma_padronizado = valor
        self.db.commit()
        self.db.refresh(isolado)
        return isolado
