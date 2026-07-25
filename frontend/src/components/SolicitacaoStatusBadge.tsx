import { StatusSolicitacao } from "../types/solicitacao";

const CONFIG: Record<StatusSolicitacao, { label: string; className: string }> = {
  AGUARDANDO_COLETA: { label: "Aguardando coleta", className: "mg-badge-alerta" },
  COLETADO: { label: "Coletado", className: "mg-badge-info" },
  EM_ANALISE: { label: "Em análise", className: "mg-badge-info" },
  LIBERADO: { label: "Liberado", className: "mg-badge-sucesso" },
  CANCELADO: { label: "Cancelado", className: "mg-badge-erro" },
};

export default function SolicitacaoStatusBadge({ status }: { status: StatusSolicitacao }) {
  const { label, className } = CONFIG[status];
  return <span className={`mg-badge ${className}`}>{label}</span>;
}
