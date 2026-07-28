import { RESULTADO_SIR_LABELS, ResultadoSIR } from "../types/antibiograma";

const CLASSNAME: Record<ResultadoSIR, string> = {
  SENSIVEL: "mg-badge-sucesso",
  INTERMEDIARIO: "mg-badge-alerta",
  RESISTENTE: "mg-badge-erro",
};

export default function ResultadoSIRBadge({ resultado }: { resultado: ResultadoSIR }) {
  return (
    <span className={`mg-badge ${CLASSNAME[resultado]}`}>{RESULTADO_SIR_LABELS[resultado]}</span>
  );
}
