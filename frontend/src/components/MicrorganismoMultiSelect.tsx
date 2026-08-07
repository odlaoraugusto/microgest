import { useEffect, useState } from "react";
import { criarMicrorganismo, listarMicrorganismos } from "../services/microrganismoService";
import { Microrganismo } from "../types/microrganismo";

interface MicrorganismoMultiSelectProps {
  value: string[];
  onChange: (ids: string[]) => void;
}

export default function MicrorganismoMultiSelect({
  value,
  onChange,
}: MicrorganismoMultiSelectProps) {
  const [opcoes, setOpcoes] = useState<Microrganismo[]>([]);
  const [carregando, setCarregando] = useState(true);
  const [novoNome, setNovoNome] = useState("");
  const [criando, setCriando] = useState(false);

  async function carregar() {
    setCarregando(true);
    const res = await listarMicrorganismos();
    setOpcoes(res.items);
    setCarregando(false);
  }

  // Carrega o catálogo de microrganismos uma vez, na montagem do seletor.
  useEffect(() => {
    carregar();
  }, []);

  function toggle(id: string) {
    if (value.includes(id)) {
      onChange(value.filter((v) => v !== id));
    } else {
      onChange([...value, id]);
    }
  }

  async function handleCriarRapido() {
    if (!novoNome.trim()) return;
    setCriando(true);
    try {
      // Não envia gram/tipo/etc. de propósito - deixa o backend tentar
      // herdar a taxonomia de outra espécie já cadastrada do mesmo gênero
      // (ver MicrorganismoFormData). Se não achar, cai nos defaults.
      const criado = await criarMicrorganismo({ nome: novoNome.trim() });
      setNovoNome("");
      await carregar();
      onChange([...value, criado.id]);
    } catch {
      // Nome provavelmente já existe no catálogo - ignora silenciosamente
    } finally {
      setCriando(false);
    }
  }

  return (
    <div>
      <div
        style={{
          maxHeight: 140,
          overflowY: "auto",
          border: "1px solid var(--mg-cinza-200)",
          borderRadius: "var(--mg-radius-sm)",
          padding: 10,
          display: "flex",
          flexDirection: "column",
          gap: 6,
        }}
      >
        {carregando && <span style={{ fontSize: 13, color: "var(--mg-cinza-600)" }}>Carregando...</span>}
        {!carregando && opcoes.length === 0 && (
          <span style={{ fontSize: 13, color: "var(--mg-cinza-600)" }}>
            Nenhum microrganismo cadastrado ainda.
          </span>
        )}
        {opcoes.map((m) => (
          <label key={m.id} style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 14 }}>
            <input
              type="checkbox"
              checked={value.includes(m.id)}
              onChange={() => toggle(m.id)}
            />
            {m.nome}
          </label>
        ))}
      </div>

      <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
        <input
          placeholder="Cadastrar novo microrganismo..."
          value={novoNome}
          onChange={(e) => setNovoNome(e.target.value)}
          style={{ flex: 1 }}
        />
        <button
          type="button"
          className="mg-btn mg-btn-outline"
          onClick={handleCriarRapido}
          disabled={criando}
        >
          {criando ? "..." : "+ Adicionar"}
        </button>
      </div>
    </div>
  );
}
