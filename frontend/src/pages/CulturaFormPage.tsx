import { FormEvent, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import MainLayout from "../layouts/MainLayout";
import SolicitacaoSelect from "../components/SolicitacaoSelect";
import MicrorganismoMultiSelect from "../components/MicrorganismoMultiSelect";
import { atualizarCultura, criarCultura, obterCultura } from "../services/culturaService";
import { extrairMensagemErro } from "../services/api";
import { CulturaFormData, GrupoCultura, ResultadoCultura } from "../types/cultura";

const FORM_INICIAL: CulturaFormData = {
  solicitacao_id: "",
  grupo: "CULTURA_GERAL",
  resultado: "EM_ANALISE",
  observacoes: "",
  microrganismo_ids: [],
  previsao_liberacao: "",
};

const RESULTADO_OPCOES: ResultadoCultura[] = [
  "EM_ANALISE",
  "POSITIVA",
  "NEGATIVA",
  "CONTAMINADA",
];

const GRUPO_OPCOES: { valor: GrupoCultura; label: string }[] = [
  { valor: "HEMOCULTURA", label: "Hemocultura" },
  { valor: "CULTURA_GERAL", label: "Cultura Geral" },
  { valor: "VIGILANCIA", label: "Cultura de Vigilância" },
  { valor: "BK", label: "Cultura para BK" },
  { valor: "FUNGOS", label: "Cultura para Fungos" },
];

export default function CulturaFormPage() {
  const { id } = useParams();
  const editando = Boolean(id);
  const navigate = useNavigate();

  const [form, setForm] = useState<CulturaFormData>(FORM_INICIAL);
  const [carregando, setCarregando] = useState(editando);
  const [salvando, setSalvando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    obterCultura(id)
      .then((c) =>
        setForm({
          solicitacao_id: c.solicitacao_id,
          grupo: c.grupo,
          resultado: c.resultado,
          observacoes: c.observacoes ?? "",
          microrganismo_ids: c.microrganismos.map((m) => m.microrganismo.id),
          previsao_liberacao: c.previsao_liberacao ?? "",
        })
      )
      .catch(() => setErro("Não foi possível carregar os dados da cultura."))
      .finally(() => setCarregando(false));
  }, [id]);

  function handleChange<K extends keyof CulturaFormData>(campo: K, valor: CulturaFormData[K]) {
    setForm((prev) => ({ ...prev, [campo]: valor }));
  }

  // Ao mudar o resultado para algo diferente de POSITIVA, limpa os
  // microrganismos selecionados (regra de negócio espelhada do backend).
  function handleResultadoChange(resultado: ResultadoCultura) {
    setForm((prev) => ({
      ...prev,
      resultado,
      microrganismo_ids: resultado === "POSITIVA" ? prev.microrganismo_ids : [],
    }));
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSalvando(true);
    setErro(null);
    try {
      const payload = {
        ...form,
        observacoes: form.observacoes || null,
        previsao_liberacao: form.previsao_liberacao || null,
      };
      if (editando && id) {
        const { solicitacao_id, ...resto } = payload;
        await atualizarCultura(id, resto);
      } else {
        await criarCultura(payload);
      }
      navigate("/microbiologia");
    } catch (err: unknown) {
      setErro(extrairMensagemErro(err, "Não foi possível salvar a cultura."));
    } finally {
      setSalvando(false);
    }
  }

  return (
    <MainLayout
      titulo={editando ? "Editar Cultura" : "Nova Cultura"}
      subtitulo="Cadastro de culturas e resultados"
    >
      <div className="mg-card" style={{ maxWidth: 720 }}>
        {carregando ? (
          <p style={{ color: "var(--mg-cinza-600)" }}>Carregando...</p>
        ) : (
          <form onSubmit={handleSubmit}>
            {erro && (
              <p style={{ color: "var(--mg-erro)", fontSize: 14, marginTop: 0, marginBottom: 16 }}>
                {erro}
              </p>
            )}

            <div className="mg-form-grid">
              <div className="mg-field" style={{ gridColumn: "1 / -1" }}>
                <label>Solicitação *</label>
                {editando ? (
                  <input value={form.solicitacao_id} disabled />
                ) : (
                  <SolicitacaoSelect
                    value={form.solicitacao_id}
                    onChange={(v) => handleChange("solicitacao_id", v)}
                  />
                )}
              </div>

              <div className="mg-field">
                <label>Grupo</label>
                <select
                  value={form.grupo}
                  onChange={(e) => handleChange("grupo", e.target.value as GrupoCultura)}
                >
                  {GRUPO_OPCOES.map((g) => (
                    <option key={g.valor} value={g.valor}>
                      {g.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="mg-field">
                <label>Resultado</label>
                <select
                  value={form.resultado}
                  onChange={(e) => handleResultadoChange(e.target.value as ResultadoCultura)}
                >
                  {RESULTADO_OPCOES.map((r) => (
                    <option key={r} value={r}>
                      {r}
                    </option>
                  ))}
                </select>
              </div>

              <div className="mg-field">
                <label>Previsão de liberação</label>
                <input
                  type="date"
                  value={form.previsao_liberacao ?? ""}
                  onChange={(e) => handleChange("previsao_liberacao", e.target.value)}
                />
                {!editando && (
                  <span style={{ fontSize: 12, color: "var(--mg-cinza-400)" }}>
                    Se deixar em branco, é calculada automaticamente.
                  </span>
                )}
              </div>

              {form.resultado === "POSITIVA" && (
                <div className="mg-field" style={{ gridColumn: "1 / -1" }}>
                  <label>Microrganismos isolados</label>
                  <MicrorganismoMultiSelect
                    value={form.microrganismo_ids}
                    onChange={(ids) => handleChange("microrganismo_ids", ids)}
                  />
                </div>
              )}

              <div className="mg-field" style={{ gridColumn: "1 / -1" }}>
                <label>Observações</label>
                <textarea
                  rows={3}
                  value={form.observacoes ?? ""}
                  onChange={(e) => handleChange("observacoes", e.target.value)}
                />
              </div>
            </div>

            <div style={{ display: "flex", gap: 10, marginTop: 22 }}>
              <button className="mg-btn mg-btn-primary" type="submit" disabled={salvando}>
                {salvando ? "Salvando..." : "Salvar"}
              </button>
              <button
                type="button"
                className="mg-btn mg-btn-outline"
                onClick={() => navigate("/microbiologia")}
              >
                Cancelar
              </button>
            </div>
          </form>
        )}
      </div>
    </MainLayout>
  );
}
