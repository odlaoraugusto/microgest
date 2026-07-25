"""
Repository base genérico.

Concentra operações de CRUD comuns a todas as entidades, para que os
repositories específicos de cada módulo (Pacientes, Solicitações,
Microbiologia, etc.) apenas herdem e adicionem consultas especializadas.
"""
import uuid
from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, db: Session, model: type[ModelType]):
        self.db = db
        self.model = model

    def get_by_id(self, entity_id: uuid.UUID) -> ModelType | None:
        return self.db.get(self.model, entity_id)

    def list(self, skip: int = 0, limit: int = 20) -> tuple[list[ModelType], int]:
        stmt = select(self.model).where(self.model.is_active.is_(True))
        total = len(self.db.scalars(stmt).all())
        items = (
            self.db.scalars(stmt.offset(skip).limit(limit).order_by(self.model.created_at.desc()))
            .all()
        )
        return list(items), total

    def create(self, obj_in: dict) -> ModelType:
        obj = self.model(**obj_in)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, obj: ModelType, obj_in: dict) -> ModelType:
        for field, value in obj_in.items():
            setattr(obj, field, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def soft_delete(self, obj: ModelType) -> None:
        """Exclusão lógica (soft delete), conforme padrão de segurança do projeto."""
        from datetime import datetime, timezone

        obj.is_active = False
        obj.deleted_at = datetime.now(timezone.utc)
        self.db.commit()
