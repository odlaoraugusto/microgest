import { FormEvent, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import MainLayout from "../layouts/MainLayout";
import PacienteSelect from "../components/PacienteSelect";
import {
  atualizarSolicitacao,
  criarSolicitacao,
  obterSolicitacao,
} from "../services/solicitacaoService";
import { extrairMensagemErro } from "../services/api";
import { listarMateriais } from "../services/materialService";
import { listarSetores } from "../services/setorService";
import { SolicitacaoFormData, StatusSolicitacao } from "../types/solicitacao";

const FORM_INICIAL: SolicitacaoFormData = {
  paciente_id: "",
  material: "",
  origem: "",
  prioridade: "ROTINA",
  status: "AGUARDANDO_COLETA",
  data_coleta: "",
  observacoes: "",
};

const STATUS_OPCOES: StatusSolicitacao[] = [
  "AGUARDANDO_COLETA",
  "COLETADO",
  "EM_ANALISE",
  "LIBERADO",
  "CANCELADO",
];

export default function SolicitacaoFormPage() {
  const { id } = useParams();
  const editando = Boolean(id);
  const navigate = useNavigate();

  const [form, setForm] = useState<SolicitacaoFormData>(FORM_INICIAL);
  const [carregando, setCarregando] = useState(editando);
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
    obterSolicitacao(id)
      .then((s) =>
        setForm({
          paciente_id: s.paciente_id,
          material: s.material,
          origem: s.origem ?? "",
          prioridade: s.prioridade,
          status: s.status,
          data_coleta: s.data_coleta ? s.data_coleta.slice(0, 10) : "",
          observacoes: s.observacoes ?? "",
        })
      )
      .catch(() => setErro("Não foi possível carregar os dados da solicitação."))
      .finally(() => setCarregando(false));
  }, [id]);

  function handleChange<K extends keyof SolicitacaoFormData>(
    campo: K,
    valor: SolicitacaoFormData[K]
  ) {
    setForm((prev) => ({ ...prev, [campo]: valor }));
  }

  // Ao marcar como "Coletado" sem data de coleta preenchida, sugere a data de hoje.
  function handleStatusChange(status: StatusSolicitacao) {
    setForm((prev) => ({
      ...prev,
      status,
      data_coleta:
        status === "COLETADO" && !prev.data_coleta
          ? new Date().toISOString().slice(0, 10)
          : prev.data_coleta,
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
        observacoes: form.observacoes || null,
      };
      if (editando && id) {
        // Ao editar, o paciente não pode ser trocado (regra simples de negócio)
        const { paciente_id, ...resto } = payload;
        await atualizarSolicitacao(id, resto);
      } else {
        await criarSolicitacao(payload);
      }
      navigate("/solicitacoes");
    } catch (err: unknown) {
      setErro(extrairMensagemErro(err, "Não foi possível salvar a solicitação."));
    } finally {
      setSalvando(false);
    }
  }

  return (
    <MainLayout
      titulo={editando ? "Editar Solicitação" : "Nova Solicitação"}
      subtitulo="Cadastro de solicitações"
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
                    handleChange("prioridade", e.target.value as SolicitacaoFormData["prioridade"])
                  }
                >
                  <option value="ROTINA">Rotina</option>
                  <option value="URGENTE">Urgente</option>
                  <option value="EMERGENCIA">Emergência</option>
                </select>
              </div>

              {editando && (
                <div className="mg-field">
                  <label>Status</label>
                  <select
                    value={form.status}
                    onChange={(e) => handleStatusChange(e.target.value as StatusSolicitacao)}
                  >
                    {STATUS_OPCOES.map((s) => (
                      <option key={s} value={s}>
                        {s}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              <div className="mg-field">
                <label>Data da coleta</label>
                <input
                  type="date"
                  value={form.data_coleta ?? ""}
                  onChange={(e) => handleChange("data_coleta", e.target.value)}
                />
                <span style={{ fontSize: 12, color: "var(--mg-cinza-400)" }}>
                  Usada para atribuir a solicitação, culturas e resultados ao mês correto nos
                  relatórios.
                </span>
              </div>

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
                onClick={() => navigate("/solicitacoes")}
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
