import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import MainLayout from "../layouts/MainLayout";
import SolicitacaoStatusBadge from "../components/SolicitacaoStatusBadge";
import { listarSolicitacoes, removerSolicitacao } from "../services/solicitacaoService";
import { Solicitacao, StatusSolicitacao } from "../types/solicitacao";

const STATUS_OPCOES: { value: StatusSolicitacao | ""; label: string }[] = [
  { value: "", label: "Todos os status" },
  { value: "AGUARDANDO_COLETA", label: "Aguardando coleta" },
  { value: "COLETADO", label: "Coletado" },
  { value: "EM_ANALISE", label: "Em análise" },
  { value: "LIBERADO", label: "Liberado" },
  { value: "CANCELADO", label: "Cancelado" },
];

export default function SolicitacoesPage() {
  const navigate = useNavigate();
  const [solicitacoes, setSolicitacoes] = useState<Solicitacao[]>([]);
  const [status, setStatus] = useState<StatusSolicitacao | "">("");
  const [total, setTotal] = useState(0);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);

  async function carregar() {
    setCarregando(true);
    setErro(null);
    try {
      const resultado = await listarSolicitacoes(undefined, status || undefined);
      setSolicitacoes(resultado.items);
      setTotal(resultado.total);
    } catch {
      setErro(
        "Não foi possível carregar as solicitações. Verifique se a API está rodando em " +
          "http://localhost:8000."
      );
    } finally {
      setCarregando(false);
    }
  }

  // eslint-disable-next-line react-hooks/set-state-in-effect -- recarrega a
  // lista toda vez que o filtro de status muda.
  useEffect(() => {
    carregar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [status]);

  async function handleRemover(solicitacao: Solicitacao) {
    const confirmar = window.confirm(
      `Remover a solicitação de "${solicitacao.material}" do paciente "${solicitacao.paciente?.nome ?? ""}"?`
    );
    if (!confirmar) return;
    await removerSolicitacao(solicitacao.id);
    carregar();
  }

  return (
    <MainLayout titulo="Solicitações" subtitulo="Controle de solicitações e coletas">
      <div className="mg-page-header">
        <select
          value={status}
          onChange={(e) => setStatus(e.target.value as StatusSolicitacao | "")}
          style={{
            padding: "9px 12px",
            borderRadius: "var(--mg-radius-sm)",
            border: "1px solid var(--mg-cinza-200)",
            fontSize: 14,
            width: 220,
          }}
        >
          {STATUS_OPCOES.map((opcao) => (
            <option key={opcao.value} value={opcao.value}>
              {opcao.label}
            </option>
          ))}
        </select>
        <button className="mg-btn mg-btn-primary" onClick={() => navigate("/solicitacoes/nova")}>
          + Nova Solicitação
        </button>
      </div>

      <div className="mg-card">
        {erro && <p style={{ color: "var(--mg-erro)", fontSize: 14 }}>{erro}</p>}

        {!erro && carregando && <p style={{ color: "var(--mg-cinza-600)" }}>Carregando...</p>}

        {!erro && !carregando && solicitacoes.length === 0 && (
          <p style={{ color: "var(--mg-cinza-600)" }}>Nenhuma solicitação encontrada.</p>
        )}

        {!erro && !carregando && solicitacoes.length > 0 && (
          <>
            <table className="mg-table">
              <thead>
                <tr>
                  <th>Paciente</th>
                  <th>Material</th>
                  <th>Origem</th>
                  <th>Prioridade</th>
                  <th>Status</th>
                  <th>Solicitado em</th>
                  <th>Ações</th>
                </tr>
              </thead>
              <tbody>
                {solicitacoes.map((s) => (
                  <tr key={s.id}>
                    <td>{s.paciente?.nome ?? "—"}</td>
                    <td>{s.material}</td>
                    <td>{s.origem ?? "—"}</td>
                    <td>{s.prioridade}</td>
                    <td>
                      <SolicitacaoStatusBadge status={s.status} />
                    </td>
                    <td>{new Date(s.data_solicitacao).toLocaleDateString("pt-BR")}</td>
                    <td style={{ display: "flex", gap: 8 }}>
                      <button
                        className="mg-btn mg-btn-outline"
                        onClick={() => navigate(`/solicitacoes/${s.id}/editar`)}
                      >
                        Editar
                      </button>
                      <button
                        className="mg-btn mg-btn-outline"
                        style={{ color: "var(--mg-erro)" }}
                        onClick={() => handleRemover(s)}
                      >
                        Remover
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <p style={{ marginTop: 14, fontSize: 13, color: "var(--mg-cinza-600)" }}>
              {total} solicitaç{total !== 1 ? "ões" : "ão"} encontrada{total !== 1 ? "s" : ""}
            </p>
          </>
        )}
      </div>
    </MainLayout>
  );
}
