"""
Router do módulo Microbiologia - Culturas (Sprint 6).
"""
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.exceptions import NotFoundError
from app.core.response import success_response
from app.db.session import get_db
from app.models.cultura import GrupoCulturaEnum, ResultadoCulturaEnum
from app.repositories.cultura_microrganismo_repository import CulturaMicrorganismoRepository
from app.schemas.cultura import (
    CulturaCreate,
    CulturaMicrorganismoOut,
    CulturaOut,
    CulturaParcialOut,
    CulturaUpdate,
    IsoladoSemAntibiogramaIn,
)
from app.services.cultura_service import CulturaService

router = APIRouter(
    prefix="/api/microbiologia", tags=["Microbiologia"], dependencies=[Depends(get_current_user)]
)


@router.get("/culturas")
def listar_culturas(
    solicitacao_id: uuid.UUID | None = Query(default=None),
    resultado: ResultadoCulturaEnum | None = Query(default=None),
    grupo: GrupoCulturaEnum | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = CulturaService(db)
    items, total = service.listar(
        solicitacao_id, resultado, grupo=grupo, page=page, page_size=page_size
    )
    data = {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [CulturaOut.model_validate(item).model_dump(mode="json") for item in items],
    }
    return success_response(data, message="Culturas listadas com sucesso.")


@router.get("/culturas/parciais")
def listar_resultados_parciais(db: Session = Depends(get_db)):
    """
    Culturas ainda "em andamento" (não liberadas), com a previsão de
    liberação e o motivo da pendência - base do relatório de resultados
    parciais.
    """
    service = CulturaService(db)
    itens = service.resultados_parciais()
    resultado = [
        CulturaParcialOut(
            **CulturaOut.model_validate(cultura).model_dump(mode="json"), pendencia=pendencia
        ).model_dump(mode="json")
        for cultura, pendencia in itens
    ]
    return success_response(
        {"total": len(resultado), "items": resultado},
        message="Resultados parciais listados com sucesso.",
    )


@router.get("/culturas/{cultura_id}")
def obter_cultura(cultura_id: uuid.UUID, db: Session = Depends(get_db)):
    service = CulturaService(db)
    cultura = service.obter(cultura_id)
    return success_response(
        CulturaOut.model_validate(cultura).model_dump(mode="json"),
        message="Cultura encontrada.",
    )


@router.post("/culturas", status_code=201)
def criar_cultura(dados: CulturaCreate, db: Session = Depends(get_db)):
    service = CulturaService(db)
    cultura = service.criar(dados)
    return success_response(
        CulturaOut.model_validate(cultura).model_dump(mode="json"),
        message="Cultura cadastrada com sucesso.",
    )


@router.put("/culturas/{cultura_id}")
def atualizar_cultura(cultura_id: uuid.UUID, dados: CulturaUpdate, db: Session = Depends(get_db)):
    service = CulturaService(db)
    cultura = service.atualizar(cultura_id, dados)
    return success_response(
        CulturaOut.model_validate(cultura).model_dump(mode="json"),
        message="Cultura atualizada com sucesso.",
    )


@router.post("/culturas/{cultura_id}/liberar")
def liberar_cultura(cultura_id: uuid.UUID, db: Session = Depends(get_db)):
    service = CulturaService(db)
    cultura = service.liberar(cultura_id)
    return success_response(
        CulturaOut.model_validate(cultura).model_dump(mode="json"),
        message="Cultura liberada tecnicamente com sucesso.",
    )


@router.delete("/culturas/{cultura_id}")
def remover_cultura(cultura_id: uuid.UUID, db: Session = Depends(get_db)):
    service = CulturaService(db)
    service.remover(cultura_id)
    return success_response(message="Cultura removida com sucesso.")


@router.put("/isolados/{isolado_id}/sem-antibiograma")
def marcar_isolado_sem_antibiograma(
    isolado_id: uuid.UUID, dados: IsoladoSemAntibiogramaIn, db: Session = Depends(get_db)
):
    """
    Marca (ou desmarca) um isolado como "sem antibiograma padronizado
    (BrCAST)" - dispensa esse isolado específico da exigência de
    antibiograma completo ao liberar a cultura (útil para microrganismos
    sem protocolo BrCAST definido).
    """
    repository = CulturaMicrorganismoRepository(db)
    isolado = repository.marcar_sem_antibiograma(
        isolado_id, dados.sem_antibiograma_padronizado
    )
    if not isolado:
        raise NotFoundError("Isolado (microrganismo da cultura) não encontrado.")
    return success_response(
        CulturaMicrorganismoOut.model_validate(isolado).model_dump(mode="json"),
        message="Isolado atualizado com sucesso.",
    )
