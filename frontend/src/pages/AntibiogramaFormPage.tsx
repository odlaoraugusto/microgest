import { FormEvent, useEffect, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import MainLayout from "../layouts/MainLayout";
import IsoladoSelect from "../components/IsoladoSelect";
import ResultadosSIREditor from "../components/ResultadosSIREditor";
import {
  atualizarAntibiograma,
  criarAntibiograma,
  obterAntibiograma,
} from "../services/antibiogramaService";
import { extrairMensagemErro } from "../services/api";
import { AntibiogramaFormData } from "../types/antibiograma";

const FORM_INICIAL: AntibiogramaFormData = {
  cultura_microrganismo_id: "",
  observacoes: "",
  resultados: [],
};

export default function AntibiogramaFormPage() {
  const { id } = useParams();
  const editando = Boolean(id);
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const isoladoId = searchParams.get("isolado_id");
  const voltarPara = searchParams.get("voltar_para");
  // Veio de um exame (fluxo unificado): o isolado já está determinado pela
  // query string, não precisa (nem deve) ser escolhido de novo no formulário.
  const isoladoPreSelecionado = Boolean(!editando && isoladoId);

  const [form, setForm] = useState<AntibiogramaFormData>(
    isoladoPreSelecionado ? { ...FORM_INICIAL, cultura_microrganismo_id: isoladoId! } : FORM_INICIAL
  );
  const [carregando, setCarregando] = useState(editando);
  const [salvando, setSalvando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    obterAntibiograma(id)
      .then((a) =>
        setForm({
          cultura_microrganismo_id: a.cultura_microrganismo_id,
          observacoes: a.observacoes ?? "",
          resultados: a.resultados.map((r) => ({
            antimicrobiano_id: r.antimicrobiano.id,
            resultado: r.resultado,
          })),
        })
      )
      .catch(() => setErro("Não foi possível carregar os dados do antibiograma."))
      .finally(() => setCarregando(false));
  }, [id]);

  function irParaDestinoFinal() {
    if (voltarPara) {
      navigate(`/exames/${voltarPara}/editar`);
    } else {
      navigate("/antibiogramas");
    }
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSalvando(true);
    setErro(null);
    try {
      const payload = { ...form, observacoes: form.observacoes || null };
      if (editando && id) {
        const { cultura_microrganismo_id, ...resto } = payload;
        await atualizarAntibiograma(id, resto);
      } else {
        await criarAntibiograma(payload);
      }
      irParaDestinoFinal();
    } catch (err: unknown) {
      setErro(extrairMensagemErro(err, "Não foi possível salvar o antibiograma."));
    } finally {
      setSalvando(false);
    }
  }

  return (
    <MainLayout
      titulo={editando ? "Editar Antibiograma" : "Novo Antibiograma"}
      subtitulo="Cadastro de perfis de sensibilidade"
    >
      <div className="mg-card" style={{ maxWidth: 780 }}>
        {carregando ? (
          <p style={{ color: "var(--mg-cinza-600)" }}>Carregando...</p>
        ) : (
          <form onSubmit={handleSubmit}>
            {erro && (
              <p style={{ color: "var(--mg-erro)", fontSize: 14, marginTop: 0, marginBottom: 16 }}>
                {erro}
              </p>
            )}

            <div className="mg-field" style={{ marginBottom: 16 }}>
              <label>Microrganismo isolado (cultura positiva) *</label>
              {editando ? (
                <input value={form.cultura_microrganismo_id} disabled />
              ) : isoladoPreSelecionado ? (
                <p style={{ margin: 0, fontSize: 14, color: "var(--mg-cinza-600)" }}>
                  Isolado pré-selecionado a partir do exame de origem.
                </p>
              ) : (
                <IsoladoSelect
                  value={form.cultura_microrganismo_id}
                  onChange={(v) =>
                    setForm((prev) => ({ ...prev, cultura_microrganismo_id: v }))
                  }
                />
              )}
            </div>

            <div className="mg-field" style={{ marginBottom: 16 }}>
              <label>Resultados por antimicrobiano (S/I/R)</label>
              <ResultadosSIREditor
                value={form.resultados}
                onChange={(resultados) => setForm((prev) => ({ ...prev, resultados }))}
              />
            </div>

            <div className="mg-field">
              <label>Observações</label>
              <textarea
                rows={3}
                value={form.observacoes ?? ""}
                onChange={(e) =>
                  setForm((prev) => ({ ...prev, observacoes: e.target.value }))
                }
              />
            </div>

            <div style={{ display: "flex", gap: 10, marginTop: 22 }}>
              <button className="mg-btn mg-btn-primary" type="submit" disabled={salvando}>
                {salvando ? "Salvando..." : "Salvar"}
              </button>
              <button
                type="button"
                className="mg-btn mg-btn-outline"
                onClick={irParaDestinoFinal}
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
