"""
Router do módulo Pacientes.

Responsável apenas por receber requisições HTTP e devolver respostas no
contrato padrão da API - toda regra de negócio fica no Service.
"""
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.response import success_response
from app.db.session import get_db
from app.schemas.paciente import PacienteCreate, PacienteOut, PacienteUpdate
from app.services.paciente_service import PacienteService

router = APIRouter(
    prefix="/api/pacientes", tags=["Pacientes"], dependencies=[Depends(get_current_user)]
)


@router.get("")
def listar_pacientes(
    termo: str | None = Query(default=None, description="Busca por nome ou prontuário"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = PacienteService(db)
    items, total = service.listar(termo, page=page, page_size=page_size)
    data = {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [PacienteOut.model_validate(item).model_dump(mode="json") for item in items],
    }
    return success_response(data, message="Pacientes listados com sucesso.")


@router.get("/{paciente_id}")
def obter_paciente(paciente_id: uuid.UUID, db: Session = Depends(get_db)):
    service = PacienteService(db)
    paciente = service.obter(paciente_id)
    return success_response(
        PacienteOut.model_validate(paciente).model_dump(mode="json"),
        message="Paciente encontrado.",
    )


@router.get("/prontuario/{prontuario}")
def obter_paciente_por_prontuario(prontuario: str, db: Session = Depends(get_db)):
    service = PacienteService(db)
    paciente = service.obter_por_prontuario(prontuario)
    return success_response(
        PacienteOut.model_validate(paciente).model_dump(mode="json"),
        message="Paciente encontrado.",
    )


@router.post("", status_code=201)
def criar_paciente(dados: PacienteCreate, db: Session = Depends(get_db)):
    service = PacienteService(db)
    paciente = service.criar(dados)
    return success_response(
        PacienteOut.model_validate(paciente).model_dump(mode="json"),
        message="Paciente cadastrado com sucesso.",
    )


@router.put("/{paciente_id}")
def atualizar_paciente(
    paciente_id: uuid.UUID, dados: PacienteUpdate, db: Session = Depends(get_db)
):
    service = PacienteService(db)
    paciente = service.atualizar(paciente_id, dados)
    return success_response(
        PacienteOut.model_validate(paciente).model_dump(mode="json"),
        message="Paciente atualizado com sucesso.",
    )


@router.delete("/{paciente_id}")
def remover_paciente(paciente_id: uuid.UUID, db: Session = Depends(get_db)):
    service = PacienteService(db)
    service.remover(paciente_id)
    return success_response(message="Paciente removido com sucesso.")
