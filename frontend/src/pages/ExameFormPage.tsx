import { FormEvent, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import MainLayout from "../layouts/MainLayout";
import MicrorganismoMultiSelect from "../components/MicrorganismoMultiSelect";
import ResultadosSIREditor from "../components/ResultadosSIREditor";
import { atualizarExame, criarExame, obterExame } from "../services/exameService";
import {
  atualizarAntibiograma,
  criarAntibiograma,
  listarAntibiogramas,
} from "../services/antibiogramaService";
import { marcarIsoladoSemAntibiograma } from "../services/culturaService";
import { listarMateriais } from "../services/materialService";
import { listarSetores } from "../services/setorService";
import { listarPacientes } from "../services/pacienteService";
import { extrairMensagemErro } from "../services/api";
import { useDebounce } from "../hooks/useDebounce";
import { CulturaMicrorganismo, GrupoCultura, ResultadoCultura } from "../types/cultura";
import { ExameFormData } from "../types/exame";
import { Antibiograma, ResultadoAntimicrobiano } from "../types/antibiograma";

const FORM_INICIAL: ExameFormData = {
  paciente_prontuario: "",
  paciente_nome: "",
  material: "",
  origem: "",
  prioridade: "ROTINA",
  data_coleta: "",
  observacoes_solicitacao: "",
  grupo: "CULTURA_GERAL",
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

const GRUPO_OPCOES: { valor: GrupoCultura; label: string }[] = [
  { valor: "HEMOCULTURA", label: "Hemocultura" },
  { valor: "CULTURA_GERAL", label: "Cultura Geral" },
  { valor: "VIGILANCIA", label: "Cultura de Vigilância" },
  { valor: "BK", label: "Cultura para BK" },
  { valor: "FUNGOS", label: "Cultura para Fungos" },
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
  const [resultadosPorIsolado, setResultadosPorIsolado] = useState<
    Record<string, ResultadoAntimicrobiano[]>
  >({});
  const [salvandoAntibiogramaId, setSalvandoAntibiogramaId] = useState<string | null>(null);
  const [salvoAntibiogramaId, setSalvoAntibiogramaId] = useState<string | null>(null);
  const [carregando, setCarregando] = useState(editando);
  const [carregandoAntibiogramas, setCarregandoAntibiogramas] = useState(false);
  const [salvando, setSalvando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const [materiaisCatalogo, setMateriaisCatalogo] = useState<string[]>([]);
  const [setoresCatalogo, setSetoresCatalogo] = useState<string[]>([]);
  const [buscandoPaciente, setBuscandoPaciente] = useState(false);
  const [pacienteEncontrado, setPacienteEncontrado] = useState<boolean | null>(null);
  const prontuarioDebounced = useDebounce(form.paciente_prontuario, 350);

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
          paciente_prontuario: c.solicitacao?.paciente?.prontuario ?? "",
          paciente_nome: c.solicitacao?.paciente?.nome ?? "",
          material: c.solicitacao?.material ?? "",
          origem: c.solicitacao?.origem ?? "",
          prioridade: c.solicitacao?.prioridade ?? "ROTINA",
          data_coleta: c.solicitacao?.data_coleta ? c.solicitacao.data_coleta.slice(0, 10) : "",
          observacoes_solicitacao: c.solicitacao?.observacoes ?? "",
          grupo: c.grupo,
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

  // Inicializa o editor local de S/I/R de cada isolado a partir do
  // antibiograma já carregado (se existir) - só na primeira vez que o
  // isolado aparece, pra não sobrescrever edições ainda não salvas.
  useEffect(() => {
    setResultadosPorIsolado((prev) => {
      let mudou = false;
      const novo = { ...prev };
      for (const m of microrganismosVinculados) {
        if (novo[m.id] === undefined) {
          const antibiograma = antibiogramasPorIsolado[m.id];
          novo[m.id] = antibiograma
            ? antibiograma.resultados.map((r) => ({
                antimicrobiano_id: r.antimicrobiano.id,
                resultado: r.resultado,
              }))
            : [];
          mudou = true;
        }
      }
      return mudou ? novo : prev;
    });
  }, [microrganismosVinculados, antibiogramasPorIsolado]);

  // Ao digitar o prontuário (só na criação), busca com debounce se já
  // existe um paciente com esse prontuário exato - se achar, preenche o
  // nome automaticamente; se não achar, avisa que será cadastrado um novo.
  useEffect(() => {
    if (editando) return;
    if (!prontuarioDebounced) {
      setPacienteEncontrado(null);
      return;
    }
    let cancelado = false;
    setBuscandoPaciente(true);
    listarPacientes(prontuarioDebounced, 1, 5)
      .then((res) => {
        if (cancelado) return;
        const encontrado = res.items.find((p) => p.prontuario === prontuarioDebounced);
        if (encontrado) {
          setPacienteEncontrado(true);
          setForm((prev) => ({ ...prev, paciente_nome: encontrado.nome }));
        } else {
          setPacienteEncontrado(false);
        }
      })
      .finally(() => {
        if (!cancelado) setBuscandoPaciente(false);
      });
    return () => {
      cancelado = true;
    };
  }, [prontuarioDebounced, editando]);

  async function handleToggleSemAntibiograma(isoladoId: string, valor: boolean) {
    try {
      const atualizado = await marcarIsoladoSemAntibiograma(isoladoId, valor);
      setMicrorganismosVinculados((prev) =>
        prev.map((item) => (item.id === isoladoId ? atualizado : item))
      );
    } catch (err: unknown) {
      window.alert(extrairMensagemErro(err, "Não foi possível atualizar o isolado."));
    }
  }

  async function handleSalvarAntibiograma(isolado: CulturaMicrorganismo) {
    const resultados = resultadosPorIsolado[isolado.id] ?? [];
    const antibiogramaExistente = antibiogramasPorIsolado[isolado.id];
    setSalvandoAntibiogramaId(isolado.id);
    try {
      const salvo = antibiogramaExistente
        ? await atualizarAntibiograma(antibiogramaExistente.id, { resultados })
        : await criarAntibiograma({ cultura_microrganismo_id: isolado.id, resultados });
      setAntibiogramasPorIsolado((prev) => ({ ...prev, [isolado.id]: salvo }));
      setSalvoAntibiogramaId(isolado.id);
      setTimeout(() => {
        setSalvoAntibiogramaId((atual) => (atual === isolado.id ? null : atual));
      }, 1500);
    } catch (err: unknown) {
      window.alert(extrairMensagemErro(err, "Não foi possível salvar o antibiograma."));
    } finally {
      setSalvandoAntibiogramaId(null);
    }
  }

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
        data_coleta: form.data_coleta || null,
        observacoes_solicitacao: form.observacoes_solicitacao || null,
        previsao_liberacao: form.previsao_liberacao || null,
        observacoes_cultura: form.observacoes_cultura || null,
      };
      if (editando && id) {
        const { paciente_prontuario, paciente_nome, ...resto } = payload;
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

  // Mensagem de apoio abaixo do campo Prontuário (só na criação).
  let mensagemProntuario: string | null = null;
  let corMensagemProntuario = "var(--mg-cinza-400)";
  if (!editando) {
    if (buscandoPaciente) {
      mensagemProntuario = "Buscando...";
    } else if (pacienteEncontrado === true) {
      mensagemProntuario = "Paciente já cadastrado";
      corMensagemProntuario = "var(--mg-secundaria)";
    } else if (pacienteEncontrado === false && form.paciente_prontuario.length > 0) {
      mensagemProntuario = "Paciente novo será cadastrado automaticamente";
    }
  }

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
              <div className="mg-field">
                <label>Prontuário *</label>
                {editando ? (
                  <input value={form.paciente_prontuario} disabled />
                ) : (
                  <input
                    required
                    value={form.paciente_prontuario}
                    placeholder="Número do prontuário"
                    onChange={(e) => handleChange("paciente_prontuario", e.target.value)}
                  />
                )}
                {mensagemProntuario && (
                  <span style={{ fontSize: 12, color: corMensagemProntuario }}>
                    {mensagemProntuario}
                  </span>
                )}
              </div>

              <div className="mg-field">
                <label>Paciente *</label>
                {editando ? (
                  <input value={form.paciente_nome} disabled />
                ) : (
                  <input
                    required
                    value={form.paciente_nome}
                    placeholder="Nome do paciente"
                    onChange={(e) => handleChange("paciente_nome", e.target.value)}
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
                <label>Data da coleta</label>
                <input
                  type="date"
                  value={form.data_coleta ?? ""}
                  onChange={(e) => handleChange("data_coleta", e.target.value)}
                />
                <span style={{ fontSize: 12, color: "var(--mg-cinza-400)" }}>
                  Se deixar em branco, usa a data de hoje.
                </span>
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
                <label>Exame</label>
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
                  <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                    {microrganismosVinculados.map((m) => {
                      const antibiograma = antibiogramasPorIsolado[m.id];
                      const resultados = resultadosPorIsolado[m.id] ?? [];
                      return (
                        <div
                          key={m.id}
                          style={{
                            border: "1px solid var(--mg-cinza-200)",
                            borderRadius: "var(--mg-radius-sm)",
                            padding: "12px 14px",
                          }}
                        >
                          <div
                            style={{
                              display: "flex",
                              alignItems: "center",
                              gap: 10,
                              marginBottom: 10,
                            }}
                          >
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

                          <label
                            style={{
                              display: "flex",
                              alignItems: "center",
                              gap: 6,
                              fontSize: 13,
                              marginBottom: m.sem_antibiograma_padronizado ? 0 : 10,
                            }}
                          >
                            <input
                              type="checkbox"
                              checked={m.sem_antibiograma_padronizado}
                              onChange={(e) =>
                                handleToggleSemAntibiograma(m.id, e.target.checked)
                              }
                            />
                            Sem antibiograma padronizado (BrCAST)
                          </label>

                          {!m.sem_antibiograma_padronizado && (
                            <>
                              <ResultadosSIREditor
                                value={resultados}
                                onChange={(novos) =>
                                  setResultadosPorIsolado((prev) => ({
                                    ...prev,
                                    [m.id]: novos,
                                  }))
                                }
                              />
                              <button
                                type="button"
                                className="mg-btn mg-btn-secondary"
                                style={{ marginTop: 4 }}
                                disabled={salvandoAntibiogramaId === m.id}
                                onClick={() => handleSalvarAntibiograma(m)}
                              >
                                {salvoAntibiogramaId === m.id
                                  ? "Salvo!"
                                  : salvandoAntibiogramaId === m.id
                                    ? "Salvando..."
                                    : "Salvar antibiograma"}
                              </button>
                            </>
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
