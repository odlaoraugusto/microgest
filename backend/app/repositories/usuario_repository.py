"""
Repository do módulo Usuários.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.usuario import Usuario
from app.repositories.base import BaseRepository


class UsuarioRepository(BaseRepository[Usuario]):
    def __init__(self, db: Session):
        super().__init__(db, Usuario)

    def get_by_email(self, email: str) -> Usuario | None:
        stmt = select(Usuario).where(Usuario.email.ilike(email))
        return self.db.scalars(stmt).first()

    def existe_algum_usuario(self) -> bool:
        stmt = select(Usuario.id).limit(1)
        return self.db.scalars(stmt).first() is not None
