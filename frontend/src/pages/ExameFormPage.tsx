import { FormEvent, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import MainLayout from "../layouts/MainLayout";
import PacienteSelect from "../components/PacienteSelect";
import MicrorganismoMultiSelect from "../components/MicrorganismoMultiSelect";
import { atualizarExame, criarExame, obterExame } from "../services/exameService";
import { listarAntibiogramas } from "../services/antibiogramaService";
import { listarMateriais } from "../services/materialService";
import { listarSetores } from "../services/setorService";
import { extrairMensagemErro } from "../services/api";
import { CulturaMicrorganismo, ResultadoCultura } from "../types/cultura";
import { ExameFormData } from "../types/exame";
import { Antibiograma } from "../types/antibiograma";

const FORM_INICIAL: ExameFormData = {
  paciente_id: "",
  material: "",
  origem: "",
  prioridade: "ROTINA",
  observacoes_solicitacao: "",
  resultado: "EM_ANALISE",
  microrganismo_ids: [],
  previsao_liberacao: "",
  observacoes_cultura: "",
};

const RESULTADO_OPCOES: ResultadoCultura[] = [
  "EM_ANALISE",
  "POSITIVA",
  "NEGATIVA",
  "CONTAMINADA",
];

export default function ExameFormPage() {
  const { id } = useParams();
  const editando = Boolean(id);
  const navigate = useNavigate();

  const [form, setForm] = useState<ExameFormData>(FORM_INICIAL);
  const [microrganismosVinculados, setMicrorganismosVinculados] = useState<
    CulturaMicrorganismo[]
  >([]);
  const [antibiogramasPorIsolado, setAntibiogramasPorIsolado] = useState<
    Record<string, Antibiograma | null>
  >({});
  const [carregando, setCarregando] = useState(editando);
  const [carregandoAntibiogramas, setCarregandoAntibiogramas] = useState(false);
  const [salvando, setSalvando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const [materiaisCatalogo, setMateriaisCatalogo] = useState<string[]>([]);
  const [setoresCatalogo, setSetoresCatalogo] = useState<string[]>([]);

  // Carrega as sugestões dos catálogos de material/setor uma vez, na montagem do form.
  useEffect(() => {
    listarMateriais().then((res) => setMateriaisCatalogo(res.items.map((m) => m.nome)));
    listarSetores().then((res) => setSetoresCatalogo(res.items.map((s) => s.nome)));
  }, []);

  useEffect(() => {
    if (!id) return;
    obterExame(id)
      .then((c) => {
        setForm({
          paciente_id: c.solicitacao?.paciente_id ?? "",
          material: c.solicitacao?.material ?? "",
          origem: c.solicitacao?.origem ?? "",
          prioridade: c.solicitacao?.prioridade ?? "ROTINA",
          observacoes_solicitacao: c.solicitacao?.observacoes ?? "",
          resultado: c.resultado,
          microrganismo_ids: c.microrganismos.map((m) => m.microrganismo.id),
          previsao_liberacao: c.previsao_liberacao ?? "",
          observacoes_cultura: c.observacoes ?? "",
        });
        setMicrorganismosVinculados(c.microrganismos);
      })
      .catch(() => setErro("Não foi possível carregar os dados do exame."))
      .finally(() => setCarregando(false));
  }, [id]);

  // Seção de antibiogramas: só faz sentido quando já existem microrganismos
  // isolados vinculados (id = cultura_microrganismo_id) e o resultado é
  // POSITIVA. Busca, para cada isolado, se já existe um antibiograma lançado.
  useEffect(() => {
    if (!editando || form.resultado !== "POSITIVA" || microrganismosVinculados.length === 0) {
      setAntibiogramasPorIsolado({});
      return;
    }
    let cancelado = false;
    setCarregandoAntibiogramas(true);
    Promise.all(
      microrganismosVinculados.map((m) =>
        listarAntibiogramas(m.id, 1, 1).then(
          (res) => [m.id, res.items[0] ?? null] as const
        )
      )
    )
      .then((pares) => {
        if (cancelado) return;
        setAntibiogramasPorIsolado(Object.fromEntries(pares));
      })
      .finally(() => {
        if (!cancelado) setCarregandoAntibiogramas(false);
      });
    return () => {
      cancelado = true;
    };
  }, [editando, form.resultado, microrganismosVinculados]);

  function handleChange<K extends keyof ExameFormData>(campo: K, valor: ExameFormData[K]) {
    setForm((prev) => ({ ...prev, [campo]: valor }));
  }

  // Ao mudar o resultado para algo diferente de POSITIVA, limpa os
  // microrganismos selecionados (mesma regra de negócio de CulturaFormPage).
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
        origem: form.origem || null,
        observacoes_solicitacao: form.observacoes_solicitacao || null,
        previsao_liberacao: form.previsao_liberacao || null,
        observacoes_cultura: form.observacoes_cultura || null,
      };
      if (editando && id) {
        const { paciente_id, ...resto } = payload;
        await atualizarExame(id, resto);
        navigate("/exames");
      } else {
        const criado = await criarExame(payload);
        // Cai direto na tela de edição, já pronta para lançar o
        // antibiograma quando o resultado da cultura sair.
        navigate(`/exames/${criado.id}/editar`);
      }
    } catch (err: unknown) {
      setErro(extrairMensagemErro(err, "Não foi possível salvar o exame."));
    } finally {
      setSalvando(false);
    }
  }

  const mostrarSecaoAntibiograma =
    editando && form.resultado === "POSITIVA" && microrganismosVinculados.length > 0;

  return (
    <MainLayout
      titulo={editando ? "Editar Exame" : "Novo Exame"}
      subtitulo="Solicitação e resultado de cultura em uma única tela"
    >
      <div className="mg-card" style={{ maxWidth: 820 }}>
        {carregando ? (
          <p style={{ color: "var(--mg-cinza-600)" }}>Carregando...</p>
        ) : (
          <form onSubmit={handleSubmit}>
            {erro && (
              <p style={{ color: "var(--mg-erro)", fontSize: 14, marginTop: 0, marginBottom: 16 }}>
                {erro}
              </p>
            )}

            <h3 style={{ margin: "0 0 12px 0" }}>Solicitação</h3>
            <div className="mg-form-grid">
              <div className="mg-field" style={{ gridColumn: "1 / -1" }}>
                <label>Paciente *</label>
                {editando ? (
                  <input value={form.paciente_id} disabled />
                ) : (
                  <PacienteSelect
                    value={form.paciente_id}
                    onChange={(pacienteId) => handleChange("paciente_id", pacienteId)}
                  />
                )}
              </div>

              <div className="mg-field">
                <label>Material *</label>
                <input
                  required
                  list="materiais-catalogo"
                  value={form.material}
                  placeholder="Ex.: Hemocultura, Urina, Escarro"
                  onChange={(e) => handleChange("material", e.target.value)}
                />
                <datalist id="materiais-catalogo">
                  {materiaisCatalogo.map((nome) => (
                    <option key={nome} value={nome} />
                  ))}
                </datalist>
              </div>

              <div className="mg-field">
                <label>Origem</label>
                <input
                  list="setores-catalogo"
                  value={form.origem ?? ""}
                  placeholder="Ex.: UTI, Enfermaria, Ambulatório"
                  onChange={(e) => handleChange("origem", e.target.value)}
                />
                <datalist id="setores-catalogo">
                  {setoresCatalogo.map((nome) => (
                    <option key={nome} value={nome} />
                  ))}
                </datalist>
              </div>

              <div className="mg-field">
                <label>Prioridade</label>
                <select
                  value={form.prioridade}
                  onChange={(e) =>
                    handleChange("prioridade", e.target.value as ExameFormData["prioridade"])
                  }
                >
                  <option value="ROTINA">Rotina</option>
                  <option value="URGENTE">Urgente</option>
                  <option value="EMERGENCIA">Emergência</option>
                </select>
              </div>

              <div className="mg-field" style={{ gridColumn: "1 / -1" }}>
                <label>Observações da solicitação</label>
                <textarea
                  rows={2}
                  value={form.observacoes_solicitacao ?? ""}
                  onChange={(e) => handleChange("observacoes_solicitacao", e.target.value)}
                />
              </div>
            </div>

            <hr style={{ margin: "24px 0", border: "none", borderTop: "1px solid var(--mg-cinza-200)" }} />

            <h3 style={{ margin: "0 0 12px 0" }}>Resultado da cultura</h3>
            <div className="mg-form-grid">
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
                <span style={{ fontSize: 12, color: "var(--mg-cinza-400)" }}>
                  Se deixar em branco, é calculada automaticamente.
                </span>
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
                <label>Observações da cultura</label>
                <textarea
                  rows={3}
                  value={form.observacoes_cultura ?? ""}
                  onChange={(e) => handleChange("observacoes_cultura", e.target.value)}
                />
              </div>
            </div>

            {mostrarSecaoAntibiograma && (
              <>
                <hr style={{ margin: "24px 0", border: "none", borderTop: "1px solid var(--mg-cinza-200)" }} />

                <h3 style={{ margin: "0 0 12px 0" }}>Antibiograma</h3>
                {carregandoAntibiogramas ? (
                  <p style={{ color: "var(--mg-cinza-600)" }}>Carregando...</p>
                ) : (
                  <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                    {microrganismosVinculados.map((m) => {
                      const antibiograma = antibiogramasPorIsolado[m.id];
                      return (
                        <div
                          key={m.id}
                          style={{
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "center",
                            border: "1px solid var(--mg-cinza-200)",
                            borderRadius: "var(--mg-radius-sm)",
                            padding: "10px 14px",
                          }}
                        >
                          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                            <strong style={{ fontSize: 14 }}>{m.microrganismo.nome}</strong>
                            {antibiograma && (
                              <span
                                className={`mg-badge ${
                                  antibiograma.data_liberacao ? "mg-badge-sucesso" : "mg-badge-alerta"
                                }`}
                              >
                                {antibiograma.data_liberacao ? "Liberado" : "Não liberado"}
                              </span>
                            )}
                          </div>
                          {antibiograma ? (
                            <button
                              type="button"
                              className="mg-btn mg-btn-outline"
                              onClick={() =>
                                navigate(`/antibiogramas/${antibiograma.id}/editar?voltar_para=${id}`)
                              }
                            >
                              Editar antibiograma
                            </button>
                          ) : (
                            <button
                              type="button"
                              className="mg-btn mg-btn-secondary"
                              onClick={() =>
                                navigate(`/antibiogramas/novo?isolado_id=${m.id}&voltar_para=${id}`)
                              }
                            >
                              + Lançar antibiograma
                            </button>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </>
            )}

            <div style={{ display: "flex", gap: 10, marginTop: 22 }}>
              <button className="mg-btn mg-btn-primary" type="submit" disabled={salvando}>
                {salvando ? "Salvando..." : "Salvar"}
              </button>
              <button
                type="button"
                className="mg-btn mg-btn-outline"
                onClick={() => navigate("/exames")}
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
