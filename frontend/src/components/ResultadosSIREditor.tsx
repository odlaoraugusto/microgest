import { useEffect, useState } from "react";
import { criarAntimicrobiano, listarAntimicrobianos } from "../services/antimicrobianoService";
import { Antimicrobiano } from "../types/antimicrobiano";
import { ResultadoAntimicrobiano, ResultadoSIR } from "../types/antibiograma";

interface ResultadosSIREditorProps {
  value: ResultadoAntimicrobiano[];
  onChange: (resultados: ResultadoAntimicrobiano[]) => void;
}

const SIR_OPCOES: ResultadoSIR[] = ["SENSIVEL", "INTERMEDIARIO", "RESISTENTE"];

export default function ResultadosSIREditor({ value, onChange }: ResultadosSIREditorProps) {
  const [antimicrobianos, setAntimicrobianos] = useState<Antimicrobiano[]>([]);
  const [novoNome, setNovoNome] = useState("");

  async function carregar() {
    const res = await listarAntimicrobianos();
    setAntimicrobianos(res.items);
  }

  // eslint-disable-next-line react-hooks/set-state-in-effect -- carrega o
  // catálogo de antimicrobianos uma vez, na montagem do editor.
  useEffect(() => {
    carregar();
  }, []);

  function adicionarLinha() {
    if (antimicrobianos.length === 0) return;
    const jaUsados = new Set(value.map((v) => v.antimicrobiano_id));
    const disponivel = antimicrobianos.find((a) => !jaUsados.has(a.id));
    if (!disponivel) return;
    onChange([...value, { antimicrobiano_id: disponivel.id, resultado: "SENSIVEL" }]);
  }

  function atualizarLinha(index: number, campo: keyof ResultadoAntimicrobiano, valor: string) {
    const novos = value.map((item, i) =>
      i === index ? { ...item, [campo]: valor } : item
    );
    onChange(novos);
  }

  function removerLinha(index: number) {
    onChange(value.filter((_, i) => i !== index));
  }

  async function handleCriarRapido() {
    if (!novoNome.trim()) return;
    try {
      await criarAntimicrobiano({ nome: novoNome.trim() });
      setNovoNome("");
      await carregar();
    } catch {
      // provavelmente já existe - ignora
    }
  }

  return (
    <div>
      {value.length === 0 && (
        <p style={{ fontSize: 13, color: "var(--mg-cinza-600)", margin: "0 0 8px 0" }}>
          Nenhum antimicrobiano adicionado ainda.
        </p>
      )}

      {value.map((linha, index) => (
        <div key={index} style={{ display: "flex", gap: 8, marginBottom: 8, alignItems: "center" }}>
          <select
            style={{ flex: 2 }}
            value={linha.antimicrobiano_id}
            onChange={(e) => atualizarLinha(index, "antimicrobiano_id", e.target.value)}
          >
            {antimicrobianos.map((a) => (
              <option key={a.id} value={a.id}>
                {a.nome}
              </option>
            ))}
          </select>
          <select
            style={{ flex: 1 }}
            value={linha.resultado}
            onChange={(e) => atualizarLinha(index, "resultado", e.target.value)}
          >
            {SIR_OPCOES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
          <button
            type="button"
            className="mg-btn mg-btn-outline"
            style={{ color: "var(--mg-erro)" }}
            onClick={() => removerLinha(index)}
          >
            Remover
          </button>
        </div>
      ))}

      <button
        type="button"
        className="mg-btn mg-btn-outline"
        onClick={adicionarLinha}
        disabled={antimicrobianos.length === 0}
        style={{ marginBottom: 12 }}
      >
        + Adicionar antimicrobiano
      </button>

      <div style={{ display: "flex", gap: 8 }}>
        <input
          placeholder="Cadastrar novo antimicrobiano no catálogo..."
          value={novoNome}
          onChange={(e) => setNovoNome(e.target.value)}
          style={{ flex: 1 }}
        />
        <button type="button" className="mg-btn mg-btn-outline" onClick={handleCriarRapido}>
          + Adicionar ao catálogo
        </button>
      </div>
    </div>
  );
}
