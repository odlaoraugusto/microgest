import { ResultadoSIR } from "../types/antibiograma";

const CONFIG: Record<ResultadoSIR, { label: string; className: string }> = {
  SENSIVEL: { label: "Sensível (S)", className: "mg-badge-sucesso" },
  INTERMEDIARIO: { label: "Intermediário (I)", className: "mg-badge-alerta" },
  RESISTENTE: { label: "Resistente (R)", className: "mg-badge-erro" },
};

export default function ResultadoSIRBadge({ resultado }: { resultado: ResultadoSIR }) {
  const { label, className } = CONFIG[resultado];
  return <span className={`mg-badge ${className}`}>{label}</span>;
}
