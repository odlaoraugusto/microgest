"""
Dependências de autenticação/autorização usadas pelos routers.

- get_current_user: extrai e valida o JWT do header Authorization,
  devolvendo o Usuario correspondente.
- require_perfil: fábrica de dependência para restringir um endpoint a
  um conjunto de perfis (ex.: apenas ADMIN pode gerenciar usuários).
"""
import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decodificar_access_token
from app.db.session import get_db
from app.models.usuario import PerfilUsuarioEnum, Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

CREDENCIAIS_INVALIDAS = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Credenciais inválidas ou sessão expirada.",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    token: str | None = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> Usuario:
    if not token:
        raise CREDENCIAIS_INVALIDAS

    payload = decodificar_access_token(token)
    if not payload or "sub" not in payload:
        raise CREDENCIAIS_INVALIDAS

    try:
        usuario_id = uuid.UUID(payload["sub"])
    except ValueError:
        raise CREDENCIAIS_INVALIDAS

    usuario = db.get(Usuario, usuario_id)
    if not usuario or not usuario.is_active:
        raise CREDENCIAIS_INVALIDAS

    return usuario


def require_perfil(*perfis_permitidos: PerfilUsuarioEnum):
    """Dependência que restringe o acesso a um endpoint por perfil de usuário."""

    def verificador(usuario: Usuario = Depends(get_current_user)) -> Usuario:
        if usuario.perfil not in perfis_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para acessar este recurso.",
            )
        return usuario

    return verificador
