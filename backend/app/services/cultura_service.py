"""
Service do módulo Culturas.

Regras de negócio:
- Uma cultura só pode ser criada para uma solicitação existente.
- Só é permitido informar microrganismos quando o resultado é POSITIVA.
- Uma cultura POSITIVA só pode ser liberada quando todos os microrganismos
  isolados tiverem antibiograma com resultado preenchido - até lá, ela
  permanece "em andamento" para fins de relatório de resultados parciais.
- A liberação técnica marca a data/hora automaticamente.
- A previsão de liberação, quando não informada, é calculada a partir do
  parâmetro de sistema 'prazo_solicitacao_dias'.
"""
import uuid
from datetime import date, datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import BusinessRuleError, NotFoundError
from app.models.cultura import Cultura, GrupoCulturaEnum, ResultadoCulturaEnum
from app.repositories.cultura_repository import CulturaRepository
from app.repositories.parametro_sistema_repository import ParametroSistemaRepository
from app.repositories.solicitacao_repository import SolicitacaoRepository
from app.schemas.cultura import CulturaCreate, CulturaUpdate

PRAZO_PADRAO_DIAS_FALLBACK = 2


class CulturaService:
    def __init__(self, db: Session):
        self.repository = CulturaRepository(db)
        self.solicitacao_repository = SolicitacaoRepository(db)
        self.parametro_repository = ParametroSistemaRepository(db)

    def listar(
        self,
        solicitacao_id: uuid.UUID | None,
        resultado: ResultadoCulturaEnum | None,
        grupo: GrupoCulturaEnum | None = None,
        page: int = 1,
        page_size: int = 20,
    ):
        skip = (page - 1) * page_size
        return self.repository.search(
            solicitacao_id=solicitacao_id,
            resultado=resultado,
            grupo=grupo,
            skip=skip,
            limit=page_size,
        )

    def obter(self, cultura_id: uuid.UUID):
        cultura = self.repository.get_by_id(cultura_id)
        if not cultura or not cultura.is_active:
            raise NotFoundError("Cultura não encontrada.")
        return cultura

    def _validar_microrganismos(self, resultado: ResultadoCulturaEnum, microrganismo_ids: list):
        if microrganismo_ids and resultado != ResultadoCulturaEnum.POSITIVA:
            raise BusinessRuleError(
                "Só é possível informar microrganismos quando o resultado é POSITIVA.",
                errors=[f"resultado '{resultado.value}' não permite microrganismos."],
            )

    def _calcular_previsao_padrao(self) -> date:
        prazo_dias = self.parametro_repository.get_valor_int(
            "prazo_solicitacao_dias", PRAZO_PADRAO_DIAS_FALLBACK
        )
        return date.today() + timedelta(days=prazo_dias)

    def criar(self, dados: CulturaCreate):
        solicitacao = self.solicitacao_repository.get_by_id(dados.solicitacao_id)
        if not solicitacao or not solicitacao.is_active:
            raise BusinessRuleError(
                "Solicitação informada não existe ou está inativa.",
                errors=[f"solicitacao_id '{dados.solicitacao_id}' inválida."],
            )

        self._validar_microrganismos(dados.resultado, dados.microrganismo_ids)

        cultura = self.repository.create(
            {
                "solicitacao_id": dados.solicitacao_id,
                "grupo": dados.grupo,
                "resultado": dados.resultado,
                "observacoes": dados.observacoes,
                "previsao_liberacao": dados.previsao_liberacao
                or self._calcular_previsao_padrao(),
            }
        )

        if dados.microrganismo_ids:
            self.repository.definir_microrganismos(cultura.id, dados.microrganismo_ids)

        return self.repository.get_by_id(cultura.id)

    def atualizar(self, cultura_id: uuid.UUID, dados: CulturaUpdate):
        cultura = self.obter(cultura_id)

        resultado_final = dados.resultado or cultura.resultado
        if dados.microrganismo_ids is not None:
            self._validar_microrganismos(resultado_final, dados.microrganismo_ids)

        dados_dict = dados.model_dump(exclude_unset=True, exclude={"microrganismo_ids"})
        self.repository.update(cultura, dados_dict)

        if dados.microrganismo_ids is not None:
            self.repository.definir_microrganismos(cultura_id, dados.microrganismo_ids)

        return self.repository.get_by_id(cultura_id)

    def liberar(self, cultura_id: uuid.UUID):
        cultura = self.obter(cultura_id)
        if cultura.liberado_tecnicamente:
            raise BusinessRuleError("Esta cultura já foi liberada tecnicamente.")
        if cultura.resultado == ResultadoCulturaEnum.EM_ANALISE:
            raise BusinessRuleError(
                "Não é possível liberar uma cultura que ainda está em análise.",
                errors=["defina o resultado antes de liberar."],
            )

        if cultura.resultado == ResultadoCulturaEnum.POSITIVA:
            if not cultura.microrganismos:
                raise BusinessRuleError(
                    "Cultura positiva precisa ter ao menos um microrganismo "
                    "identificado antes de ser liberada.",
                    errors=["nenhum microrganismo vinculado à cultura."],
                )
            isolados_pendentes = self.repository.isolados_sem_antibiograma(cultura)
            if isolados_pendentes:
                raise BusinessRuleError(
                    "Cultura positiva precisa ter o antibiograma preenchido para "
                    "todos os microrganismos isolados antes de ser liberada.",
                    errors=[f"{len(isolados_pendentes)} isolado(s) sem antibiograma completo."],
                )

        self.repository.update(
            cultura,
            {
                "liberado_tecnicamente": True,
                "data_liberacao": datetime.now(timezone.utc),
            },
        )
        return self.repository.get_by_id(cultura_id)

    def calcular_pendencia(self, cultura: Cultura) -> str:
        """
        Explica, em uma frase curta, por que a cultura ainda está "em
        andamento" - usado no relatório de resultados parciais.
        """
        if cultura.resultado == ResultadoCulturaEnum.EM_ANALISE:
            return "Aguardando resultado da cultura"

        if cultura.resultado == ResultadoCulturaEnum.POSITIVA:
            if not cultura.microrganismos:
                return "Aguardando identificação do microrganismo"
            if self.repository.isolados_sem_antibiograma(cultura):
                return "Aguardando antibiograma"
            return "Pronta para liberação"

        # NEGATIVA ou CONTAMINADA não dependem de microrganismo/antibiograma
        return "Pronta para liberação"

    def resultados_parciais(self) -> list[tuple[Cultura, str]]:
        """Culturas ainda em andamento, cada uma com sua pendência explicada."""
        culturas = self.repository.buscar_parciais()
        return [(cultura, self.calcular_pendencia(cultura)) for cultura in culturas]

    def remover(self, cultura_id: uuid.UUID):
        cultura = self.obter(cultura_id)
        self.repository.soft_delete(cultura)
