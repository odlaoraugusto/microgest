"""
Router do módulo de Autenticação (Sprint 12).

Usa OAuth2PasswordRequestForm (padrão do FastAPI/Swagger) no login, o
que permite inclusive testar o login diretamente pela tela do /docs.
"""
from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.rate_limit import limiter
from app.core.response import success_response
from app.db.session import get_db
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioOut
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["Autenticação"])


@router.post("/login")
@limiter.limit("5/minute")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    service = AuthService(db)
    # OAuth2PasswordRequestForm usa o campo "username" - aqui ele carrega o e-mail.
    token = service.autenticar(form_data.username, form_data.password)
    return success_response(
        {"access_token": token, "token_type": "bearer"}, message="Login realizado com sucesso."
    )


@router.get("/me")
def obter_usuario_logado(usuario_atual: Usuario = Depends(get_current_user)):
    return success_response(
        UsuarioOut.model_validate(usuario_atual).model_dump(mode="json"),
        message="Usuário autenticado.",
    )
