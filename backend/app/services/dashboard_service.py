"""
Service do Dashboard (Sprint 8).

Monta o resumo exibido na tela inicial a partir de consultas agregadas
sobre Solicitações e Culturas. Os "alertas" seguem o espírito da "IA
silenciosa" descrita no planejamento do projeto: o sistema entrega
informação pronta, sem exigir que o usuário faça perguntas.
"""
from sqlalchemy.orm import Session

from app.repositories.dashboard_repository import DashboardRepository
from app.schemas.dashboard import AlertaOut, ResumoDashboardOut, TopMicrorganismoOut


class DashboardService:
    def __init__(self, db: Session):
        self.repository = DashboardRepository(db)

    def resumo(self) -> ResumoDashboardOut:
        culturas_hoje = self.repository.contar_culturas_criadas_hoje()
        aguardando_atualizacao = self.repository.contar_solicitacoes_em_andamento()
        prazo_vencido = self.repository.contar_solicitacoes_com_prazo_vencido()
        liberados_hoje = self.repository.contar_culturas_liberadas_hoje()
        top = self.repository.top_microrganismos()
        aguardando_liberacao = self.repository.culturas_positivas_aguardando_liberacao()

        top_microrganismos = [
            TopMicrorganismoOut(nome=nome, quantidade=quantidade) for nome, quantidade in top
        ]

        alertas: list[AlertaOut] = []

        if prazo_vencido > 0:
            alertas.append(
                AlertaOut(
                    tipo="prazo",
                    mensagem=(
                        f"Existem {prazo_vencido} solicitação(ões) com prazo de "
                        f"liberação vencido."
                    ),
                )
            )

        if aguardando_liberacao > 0:
            alertas.append(
                AlertaOut(
                    tipo="info",
                    mensagem=(
                        f"Há {aguardando_liberacao} cultura(s) positiva(s) aguardando "
                        f"liberação técnica."
                    ),
                )
            )

        if top_microrganismos:
            mais_frequente = top_microrganismos[0]
            alertas.append(
                AlertaOut(
                    tipo="resistencia",
                    mensagem=(
                        f"{mais_frequente.nome} foi o microrganismo mais isolado nos "
                        f"últimos 30 dias ({mais_frequente.quantidade} ocorrência(s))."
                    ),
                )
            )

        return ResumoDashboardOut(
            culturas_hoje=culturas_hoje,
            aguardando_atualizacao=aguardando_atualizacao,
            prazo_vencido=prazo_vencido,
            liberados_hoje=liberados_hoje,
            top_microrganismos=top_microrganismos,
            alertas=alertas,
        )
