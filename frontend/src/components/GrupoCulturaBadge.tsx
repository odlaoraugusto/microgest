import { GrupoCultura } from "../types/cultura";

const CONFIG: Record<GrupoCultura, { label: string; className: string }> = {
  HEMOCULTURA: { label: "Hemocultura", className: "mg-badge-erro" },
  CULTURA_GERAL: { label: "Cultura Geral", className: "mg-badge-info" },
  VIGILANCIA: { label: "Vigilância", className: "mg-badge-alerta" },
  BK: { label: "BK", className: "mg-badge-alerta" },
  FUNGOS: { label: "Fungos", className: "mg-badge-alerta" },
};

export default function GrupoCulturaBadge({ grupo }: { grupo: GrupoCultura }) {
  const { label, className } = CONFIG[grupo];
  return <span className={`mg-badge ${className}`}>{label}</span>;
}
