import { useEffect, useState } from "react";
import { listarSolicitacoes } from "../services/solicitacaoService";
import { Solicitacao } from "../types/solicitacao";

interface SolicitacaoSelectProps {
  value: string;
  onChange: (solicitacaoId: string) => void;
}

export default function SolicitacaoSelect({ value, onChange }: SolicitacaoSelectProps) {
  const [opcoes, setOpcoes] = useState<Solicitacao[]>([]);
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    listarSolicitacoes(undefined, undefined, 1, 50)
      .then((res) => setOpcoes(res.items))
      .finally(() => setCarregando(false));
  }, []);

  return (
    <select value={value} onChange={(e) => onChange(e.target.value)} required>
      <option value="">{carregando ? "Carregando..." : "Selecione uma solicitação"}</option>
      {opcoes.map((s) => (
        <option key={s.id} value={s.id}>
          {s.material} — {s.paciente?.nome ?? "paciente"} (
          {new Date(s.data_solicitacao).toLocaleDateString("pt-BR")})
        </option>
      ))}
    </select>
  );
}
