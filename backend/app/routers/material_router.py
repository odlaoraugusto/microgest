"""
Router do catálogo de Materiais (Sprint 11).
"""
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.response import success_response
from app.db.session import get_db
from app.schemas.material import MaterialCreate, MaterialOut, MaterialUpdate
from app.services.material_service import MaterialService

router = APIRouter(
    prefix="/api/materiais", tags=["Materiais"], dependencies=[Depends(get_current_user)]
)


@router.get("")
def listar_materiais(db: Session = Depends(get_db)):
    service = MaterialService(db)
    itens = service.listar()
    data = {"total": len(itens), "items": [MaterialOut.model_validate(i).model_dump(mode="json") for i in itens]}
    return success_response(data, message="Materiais listados com sucesso.")


@router.post("", status_code=201)
def criar_material(dados: MaterialCreate, db: Session = Depends(get_db)):
    service = MaterialService(db)
    material = service.criar(dados)
    return success_response(
        MaterialOut.model_validate(material).model_dump(mode="json"), message="Material cadastrado com sucesso."
    )


@router.put("/{material_id}")
def atualizar_material(material_id: uuid.UUID, dados: MaterialUpdate, db: Session = Depends(get_db)):
    service = MaterialService(db)
    material = service.atualizar(material_id, dados)
    return success_response(
        MaterialOut.model_validate(material).model_dump(mode="json"), message="Material atualizado com sucesso."
    )


@router.delete("/{material_id}")
def remover_material(material_id: uuid.UUID, db: Session = Depends(get_db)):
    service = MaterialService(db)
    service.remover(material_id)
    return success_response(message="Material removido com sucesso.")
