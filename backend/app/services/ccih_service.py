"""
Service do módulo CCIH (Sprint 9).

Por padrão, os indicadores são calculados sobre o mês corrente, mas o
período pode ser customizado (usado pelo Relatório mensal automático e
por consultas ad-hoc da comissão).
"""
from datetime import date

from sqlalchemy.orm import Session

from app.models.cultura import ResultadoCulturaEnum
from app.repositories.ccih_repository import CCIHRepository
from app.schemas.ccih import (
    DistribuicaoSetorOut,
    IndicadoresCCIHOut,
    PerfilMicrobiologicoOut,
    TaxaResistenciaOut,
)


def _primeiro_dia_do_mes(referencia: date) -> date:
    return referencia.replace(day=1)


class CCIHService:
    def __init__(self, db: Session):
        self.repository = CCIHRepository(db)

    def indicadores(
        self, data_inicio: date | None = None, data_fim: date | None = None
    ) -> IndicadoresCCIHOut:
        hoje = date.today()
        inicio = data_inicio or _primeiro_dia_do_mes(hoje)
        fim = data_fim or hoje

        total_solicitacoes = self.repository.total_solicitacoes(inicio, fim)

        total_finalizadas = self.repository.total_culturas_por_resultado(inicio, fim)
        total_positivas = self.repository.total_culturas_por_resultado(
            inicio, fim, resultado=ResultadoCulturaEnum.POSITIVA
        )

        taxa_positividade = (
            round((total_positivas / total_finalizadas) * 100, 1)
            if total_finalizadas > 0
            else 0.0
        )

        distribuicao_raw = self.repository.distribuicao_por_setor(inicio, fim)
        distribuicao = [
            DistribuicaoSetorOut(setor=setor, total_positivas=total)
            for setor, total in distribuicao_raw
        ]

        perfil_raw = self.repository.perfil_microbiologico(inicio, fim)
        total_isolados = sum(qtd for _, qtd in perfil_raw)
        perfil = [
            PerfilMicrobiologicoOut(
                microrganismo=nome,
                quantidade=quantidade,
                percentual=round((quantidade / total_isolados) * 100, 1)
                if total_isolados > 0
                else 0.0,
            )
            for nome, quantidade in perfil_raw
        ]

        resistencia_raw = self.repository.taxa_resistencia(inicio, fim)
        resistencia = [
            TaxaResistenciaOut(
                antimicrobiano=nome,
                total_testado=testado,
                total_resistente=resistente,
                percentual_resistente=round((resistente / testado) * 100, 1)
                if testado > 0
                else 0.0,
                total_sensivel=sensivel,
                percentual_sensivel=round((sensivel / testado) * 100, 1)
                if testado > 0
                else 0.0,
            )
            for nome, testado, resistente, sensivel in resistencia_raw
        ]

        return IndicadoresCCIHOut(
            periodo_inicio=inicio,
            periodo_fim=fim,
            total_solicitacoes=total_solicitacoes,
            total_culturas_positivas=total_positivas,
            taxa_positividade=taxa_positividade,
            distribuicao_por_setor=distribuicao,
            perfil_microbiologico=perfil,
            taxa_resistencia=resistencia,
        )
