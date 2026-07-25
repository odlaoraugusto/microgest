"""
Service do módulo Solicitações.

Regra de negócio principal: uma solicitação só pode ser criada para um
paciente existente e ativo. O avanço de status também segue uma ordem
lógica simples (não é permitido "voltar" de LIBERADO/CANCELADO).
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import BusinessRuleError, NotFoundError
from app.repositories.paciente_repository import PacienteRepository
from app.repositories.solicitacao_repository import SolicitacaoRepository
from app.models.solicitacao import StatusSolicitacaoEnum
from app.schemas.solicitacao import SolicitacaoCreate, SolicitacaoUpdate

STATUS_FINALIZADOS = {StatusSolicitacaoEnum.LIBERADO, StatusSolicitacaoEnum.CANCELADO}


class SolicitacaoService:
    def __init__(self, db: Session):
        self.repository = SolicitacaoRepository(db)
        self.paciente_repository = PacienteRepository(db)

    def listar(
        self,
        paciente_id: uuid.UUID | None,
        status: StatusSolicitacaoEnum | None,
        page: int = 1,
        page_size: int = 20,
    ):
        skip = (page - 1) * page_size
        items, total = self.repository.search(
            paciente_id=paciente_id, status=status, skip=skip, limit=page_size
        )
        return items, total

    def obter(self, solicitacao_id: uuid.UUID):
        solicitacao = self.repository.get_by_id(solicitacao_id)
        if not solicitacao or not solicitacao.is_active:
            raise NotFoundError("Solicitação não encontrada.")
        return solicitacao

    def criar(self, dados: SolicitacaoCreate):
        paciente = self.paciente_repository.get_by_id(dados.paciente_id)
        if not paciente or not paciente.is_active:
            raise BusinessRuleError(
                "Paciente informado não existe ou está inativo.",
                errors=[f"paciente_id '{dados.paciente_id}' inválido."],
            )

        payload = dados.model_dump()
        if not payload.get("data_solicitacao"):
            from datetime import date

            payload["data_solicitacao"] = date.today()

        solicitacao = self.repository.create(payload)
        return self.repository.get_by_id(solicitacao.id)

    def atualizar(self, solicitacao_id: uuid.UUID, dados: SolicitacaoUpdate):
        solicitacao = self.obter(solicitacao_id)

        if solicitacao.status in STATUS_FINALIZADOS and dados.status:
            raise BusinessRuleError(
                "Não é possível alterar o status de uma solicitação já "
                "liberada ou cancelada.",
                errors=[f"status atual '{solicitacao.status.value}' é final."],
            )

        dados_dict = dados.model_dump(exclude_unset=True)

        # Marca automaticamente a data/hora de coleta ao mudar para COLETADO,
        # se o cliente não enviou uma data explicitamente.
        if dados_dict.get("status") == StatusSolicitacaoEnum.COLETADO and not dados_dict.get(
            "data_coleta"
        ):
            dados_dict["data_coleta"] = datetime.now(timezone.utc)

        self.repository.update(solicitacao, dados_dict)
        return self.repository.get_by_id(solicitacao_id)

    def remover(self, solicitacao_id: uuid.UUID):
        solicitacao = self.obter(solicitacao_id)
        self.repository.soft_delete(solicitacao)
