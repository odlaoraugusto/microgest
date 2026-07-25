import { useEffect, useState } from "react";
import { listarCulturas } from "../services/culturaService";
import { Cultura } from "../types/cultura";

interface IsoladoSelectProps {
  value: string;
  onChange: (culturaMicrorganismoId: string) => void;
}

/**
 * Um "isolado" é a combinação (cultura positiva, microrganismo
 * específico) - representado pelo id do CulturaMicrorganismo. Como uma
 * cultura pode ser polimicrobiana, listamos cada microrganismo isolado
 * separadamente como uma opção própria.
 */
export default function IsoladoSelect({ value, onChange }: IsoladoSelectProps) {
  const [culturas, setCulturas] = useState<Cultura[]>([]);
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    listarCulturas(undefined, 1, 100)
      .then((res) => setCulturas(res.items.filter((c) => c.resultado === "POSITIVA")))
      .finally(() => setCarregando(false));
  }, []);

  const opcoes = culturas.flatMap((c) =>
    c.microrganismos.map((m) => ({
      id: m.id,
      label: `${m.microrganismo.nome} — ${c.solicitacao?.paciente?.nome ?? "paciente"} (${
        c.solicitacao?.material ?? "material"
      })`,
    }))
  );

  return (
    <select value={value} onChange={(e) => onChange(e.target.value)} required>
      <option value="">
        {carregando ? "Carregando..." : "Selecione o microrganismo isolado"}
      </option>
      {opcoes.map((o) => (
        <option key={o.id} value={o.id}>
          {o.label}
        </option>
      ))}
      {!carregando && opcoes.length === 0 && (
        <option value="" disabled>
          Nenhuma cultura positiva com microrganismo cadastrado ainda
        </option>
      )}
    </select>
  );
}
