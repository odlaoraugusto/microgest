"""
Router do módulo Usuários.

Regra especial de bootstrap: a criação do usuário está aberta (sem
autenticação) apenas enquanto não existir nenhum usuário no sistema -
esse primeiro cadastro vira automaticamente ADMIN (ver UsuarioService).
A partir daí, criar/listar/editar/remover usuários exige um ADMIN
autenticado.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, oauth2_scheme, require_perfil
from app.core.response import success_response
from app.db.session import get_db
from app.models.usuario import PerfilUsuarioEnum
from app.schemas.usuario import UsuarioCreate, UsuarioOut, UsuarioUpdate
from app.services.usuario_service import UsuarioService

router = APIRouter(prefix="/api/usuarios", tags=["Usuários"])


@router.post("", status_code=201)
def criar_usuario(
    dados: UsuarioCreate,
    db: Session = Depends(get_db),
    token: str | None = Depends(oauth2_scheme),
):
    service = UsuarioService(db)

    if not service.sistema_precisa_de_bootstrap():
        usuario_atual = get_current_user(token=token, db=db)
        if usuario_atual.perfil != PerfilUsuarioEnum.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Apenas administradores podem cadastrar novos usuários.",
            )

    usuario = service.criar(dados)
    return success_response(
        UsuarioOut.model_validate(usuario).model_dump(mode="json"),
        message="Usuário cadastrado com sucesso.",
    )


@router.get("", dependencies=[Depends(require_perfil(PerfilUsuarioEnum.ADMIN))])
def listar_usuarios(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = UsuarioService(db)
    items, total = service.listar(page=page, page_size=page_size)
    data = {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [UsuarioOut.model_validate(item).model_dump(mode="json") for item in items],
    }
    return success_response(data, message="Usuários listados com sucesso.")


@router.put("/{usuario_id}", dependencies=[Depends(require_perfil(PerfilUsuarioEnum.ADMIN))])
def atualizar_usuario(usuario_id: uuid.UUID, dados: UsuarioUpdate, db: Session = Depends(get_db)):
    service = UsuarioService(db)
    usuario = service.atualizar(usuario_id, dados)
    return success_response(
        UsuarioOut.model_validate(usuario).model_dump(mode="json"),
        message="Usuário atualizado com sucesso.",
    )


@router.delete("/{usuario_id}", dependencies=[Depends(require_perfil(PerfilUsuarioEnum.ADMIN))])
def remover_usuario(usuario_id: uuid.UUID, db: Session = Depends(get_db)):
    service = UsuarioService(db)
    service.remover(usuario_id)
    return success_response(message="Usuário removido com sucesso.")
