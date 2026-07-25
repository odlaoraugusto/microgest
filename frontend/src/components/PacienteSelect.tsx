import { useEffect, useState } from "react";
import { useDebounce } from "../hooks/useDebounce";
import { listarPacientes } from "../services/pacienteService";
import { Paciente } from "../types/paciente";

interface PacienteSelectProps {
  value: string;
  onChange: (pacienteId: string) => void;
}

export default function PacienteSelect({ value, onChange }: PacienteSelectProps) {
  const [termo, setTermo] = useState("");
  const [opcoes, setOpcoes] = useState<Paciente[]>([]);
  const [carregando, setCarregando] = useState(false);
  const termoDebounced = useDebounce(termo, 350);

  // busca (com debounce) toda vez que o termo digitado muda.
  useEffect(() => {
    setCarregando(true);
    listarPacientes(termoDebounced || undefined, 1, 20)
      .then((res) => setOpcoes(res.items))
      .finally(() => setCarregando(false));
  }, [termoDebounced]);

  return (
    <div>
      <input
        placeholder="Buscar paciente por nome ou prontuário..."
        value={termo}
        onChange={(e) => setTermo(e.target.value)}
        style={{ marginBottom: 6 }}
      />
      <select value={value} onChange={(e) => onChange(e.target.value)} required>
        <option value="">
          {carregando ? "Carregando..." : "Selecione um paciente"}
        </option>
        {opcoes.map((p) => (
          <option key={p.id} value={p.id}>
            {p.nome} — prontuário {p.prontuario}
          </option>
        ))}
      </select>
    </div>
  );
}
