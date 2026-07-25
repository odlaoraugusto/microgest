import { ResultadoCultura } from "../types/cultura";

const CONFIG: Record<ResultadoCultura, { label: string; className: string }> = {
  EM_ANALISE: { label: "Em análise", className: "mg-badge-info" },
  POSITIVA: { label: "Positiva", className: "mg-badge-erro" },
  NEGATIVA: { label: "Negativa", className: "mg-badge-sucesso" },
  CONTAMINADA: { label: "Contaminada", className: "mg-badge-alerta" },
};

export default function ResultadoCulturaBadge({
  resultado,
}: {
  resultado: ResultadoCultura;
}) {
  const { label, className } = CONFIG[resultado];
  return <span className={`mg-badge ${className}`}>{label}</span>;
}
