"""
Router do módulo Configurações - Parâmetros do Sistema (Sprint 11).

A gestão de Usuários vive em app/routers/usuario_router.py
(/api/usuarios). Catálogos (Microrganismos, Antimicrobianos) vivem em
seus próprios routers, já criados nas Sprints 6 e 7. Este router cuida
apenas dos parâmetros de configuração propriamente ditos.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import require_perfil
from app.core.response import success_response
from app.db.session import get_db
from app.models.usuario import PerfilUsuarioEnum
from app.schemas.parametro_sistema import ParametroSistemaOut, ParametroSistemaUpdate
from app.services.parametro_sistema_service import ParametroSistemaService

router = APIRouter(prefix="/api/configuracoes", tags=["Configurações"])


@router.get("/parametros")
def listar_parametros(db: Session = Depends(get_db)):
    service = ParametroSistemaService(db)
    parametros = service.listar()
    data = [ParametroSistemaOut.model_validate(p).model_dump(mode="json") for p in parametros]
    return success_response(data, message="Parâmetros do sistema listados com sucesso.")


@router.put(
    "/parametros/{chave}",
    dependencies=[Depends(require_perfil(PerfilUsuarioEnum.ADMIN))],
)
def atualizar_parametro(chave: str, dados: ParametroSistemaUpdate, db: Session = Depends(get_db)):
    service = ParametroSistemaService(db)
    parametro = service.atualizar(chave, dados.valor)
    return success_response(
        ParametroSistemaOut.model_validate(parametro).model_dump(mode="json"),
        message="Parâmetro atualizado com sucesso.",
    )
