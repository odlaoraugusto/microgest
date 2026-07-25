import { StatusInternacao } from "../types/paciente";

const CONFIG: Record<StatusInternacao, { label: string; className: string }> = {
  INTERNADO: { label: "Internado", className: "mg-badge-alerta" },
  AMBULATORIAL: { label: "Ambulatorial", className: "mg-badge-info" },
  ALTA: { label: "Alta", className: "mg-badge-sucesso" },
  OBITO: { label: "Óbito", className: "mg-badge-erro" },
};

export default function StatusBadge({ status }: { status: StatusInternacao }) {
  const { label, className } = CONFIG[status];
  return <span className={`mg-badge ${className}`}>{label}</span>;
}
