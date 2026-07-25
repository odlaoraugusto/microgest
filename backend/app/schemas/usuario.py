"""
Schemas de validação de entrada/saída do módulo Usuários.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.usuario import PerfilUsuarioEnum


class UsuarioCreate(BaseModel):
    nome: str = Field(..., min_length=2, max_length=200)
    email: EmailStr
    senha: str = Field(..., min_length=8, max_length=100)
    perfil: PerfilUsuarioEnum = PerfilUsuarioEnum.VISUALIZADOR


class UsuarioUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=2, max_length=200)
    perfil: PerfilUsuarioEnum | None = None
    senha: str | None = Field(default=None, min_length=8, max_length=100)


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nome: str
    email: str
    perfil: PerfilUsuarioEnum
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UsuarioListOut(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[UsuarioOut]
