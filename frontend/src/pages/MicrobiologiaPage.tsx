import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import MainLayout from "../layouts/MainLayout";
import ResultadoCulturaBadge from "../components/ResultadoCulturaBadge";
import GrupoCulturaBadge from "../components/GrupoCulturaBadge";
import {
  liberarCultura,
  listarCulturas,
  listarResultadosParciais,
  removerCultura,
} from "../services/culturaService";
import { extrairMensagemErro } from "../services/api";
import { Cultura, CulturaParcial } from "../types/cultura";

type Visao = "todas" | "andamento";

function formatarData(iso: string | null) {
  if (!iso) return "—";
  return new Date(`${iso}T00:00:00`).toLocaleDateString("pt-BR");
}

export default function MicrobiologiaPage() {
  const navigate = useNavigate();
  const [visao, setVisao] = useState<Visao>("todas");
  const [culturas, setCulturas] = useState<Cultura[]>([]);
  const [parciais, setParciais] = useState<CulturaParcial[]>([]);
  const [total, setTotal] = useState(0);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);

  async function carregar() {
    setCarregando(true);
    setErro(null);
    try {
      if (visao === "todas") {
        const resultado = await listarCulturas();
        setCulturas(resultado.items);
        setTotal(resultado.total);
      } else {
        const resultado = await listarResultadosParciais();
        setParciais(resultado.items);
        setTotal(resultado.total);
      }
    } catch {
      setErro(
        "Não foi possível carregar as culturas. Verifique se a API está rodando em " +
          "http://localhost:8000."
      );
    } finally {
      setCarregando(false);
    }
  }

  // Recarrega a lista toda vez que a visão (Todas / Em andamento) muda.
  useEffect(() => {
    carregar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [visao]);

  async function handleLiberar(cultura: Cultura) {
    try {
      await liberarCultura(cultura.id);
      carregar();
    } catch (err: unknown) {
      window.alert(extrairMensagemErro(err, "Não foi possível liberar a cultura."));
    }
  }

  async function handleRemover(cultura: Cultura) {
    const confirmar = window.confirm(
      `Remover a cultura da solicitação "${cultura.solicitacao?.material ?? ""}"?`
    );
    if (!confirmar) return;
    await removerCultura(cultura.id);
    carregar();
  }

  return (
    <MainLayout titulo="Microbiologia" subtitulo="Culturas e resultados">
      <div className="mg-page-header">
        <div style={{ display: "flex", gap: 8 }}>
          <button
            className={`mg-btn ${visao === "todas" ? "mg-btn-primary" : "mg-btn-outline"}`}
            onClick={() => setVisao("todas")}
          >
            Todas
          </button>
          <button
            className={`mg-btn ${visao === "andamento" ? "mg-btn-primary" : "mg-btn-outline"}`}
            onClick={() => setVisao("andamento")}
          >
            Em andamento
          </button>
        </div>
        <button className="mg-btn mg-btn-primary" onClick={() => navigate("/microbiologia/nova")}>
          + Nova Cultura
        </button>
      </div>

      <div className="mg-card">
        {erro && <p style={{ color: "var(--mg-erro)", fontSize: 14 }}>{erro}</p>}
        {!erro && carregando && <p style={{ color: "var(--mg-cinza-600)" }}>Carregando...</p>}

        {/* ----- Visão: Todas as culturas ----- */}
        {!erro && !carregando && visao === "todas" && culturas.length === 0 && (
          <p style={{ color: "var(--mg-cinza-600)" }}>Nenhuma cultura cadastrada.</p>
        )}

        {!erro && !carregando && visao === "todas" && culturas.length > 0 && (
          <>
            <table className="mg-table">
              <thead>
                <tr>
                  <th>Paciente</th>
                  <th>Material</th>
                  <th>Grupo</th>
                  <th>Resultado</th>
                  <th>Microrganismos</th>
                  <th>Liberada</th>
                  <th>Ações</th>
                </tr>
              </thead>
              <tbody>
                {culturas.map((c) => (
                  <tr key={c.id}>
                    <td>{c.solicitacao?.paciente?.nome ?? "—"}</td>
                    <td>{c.solicitacao?.material ?? "—"}</td>
                    <td>
                      <GrupoCulturaBadge grupo={c.grupo} />
                    </td>
                    <td>
                      <ResultadoCulturaBadge resultado={c.resultado} />
                    </td>
                    <td>
                      {c.microrganismos.length > 0
                        ? c.microrganismos.map((m) => m.microrganismo.nome).join(", ")
                        : "—"}
                    </td>
                    <td>
                      {c.liberado_tecnicamente ? (
                        <span className="mg-badge mg-badge-sucesso">Sim</span>
                      ) : (
                        <span className="mg-badge mg-badge-alerta">Não</span>
                      )}
                    </td>
                    <td style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                      <button
                        className="mg-btn mg-btn-outline"
                        onClick={() => navigate(`/microbiologia/${c.id}/editar`)}
                      >
                        Editar
                      </button>
                      {!c.liberado_tecnicamente && c.resultado !== "EM_ANALISE" && (
                        <button
                          className="mg-btn mg-btn-secondary"
                          onClick={() => handleLiberar(c)}
                        >
                          Liberar
                        </button>
                      )}
                      <button
                        className="mg-btn mg-btn-outline"
                        style={{ color: "var(--mg-erro)" }}
                        onClick={() => handleRemover(c)}
                      >
                        Remover
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <p style={{ marginTop: 14, fontSize: 13, color: "var(--mg-cinza-600)" }}>
              {total} cultura{total !== 1 ? "s" : ""} encontrada{total !== 1 ? "s" : ""}
            </p>
          </>
        )}

        {/* ----- Visão: Resultados parciais (em andamento) ----- */}
        {!erro && !carregando && visao === "andamento" && parciais.length === 0 && (
          <p style={{ color: "var(--mg-cinza-600)" }}>
            Nenhuma cultura em andamento no momento - tudo liberado! 🎉
          </p>
        )}

        {!erro && !carregando && visao === "andamento" && parciais.length > 0 && (
          <>
            <p style={{ color: "var(--mg-cinza-600)", fontSize: 13, marginTop: -4, marginBottom: 16 }}>
              Culturas que ainda não foram liberadas, com a previsão de liberação e o que
              está pendente. Para exportar em Excel, use a página de Relatórios.
            </p>
            <table className="mg-table">
              <thead>
                <tr>
                  <th>Paciente</th>
                  <th>Material</th>
                  <th>Grupo</th>
                  <th>Resultado Atual</th>
                  <th>Previsão de Liberação</th>
                  <th>Pendência</th>
                  <th>Ações</th>
                </tr>
              </thead>
              <tbody>
                {parciais.map((c) => (
                  <tr key={c.id}>
                    <td>{c.solicitacao?.paciente?.nome ?? "—"}</td>
                    <td>{c.solicitacao?.material ?? "—"}</td>
                    <td>
                      <GrupoCulturaBadge grupo={c.grupo} />
                    </td>
                    <td>
                      <ResultadoCulturaBadge resultado={c.resultado} />
                    </td>
                    <td>{formatarData(c.previsao_liberacao)}</td>
                    <td>
                      <span
                        className={`mg-badge ${
                          c.pendencia === "Pronta para liberação"
                            ? "mg-badge-sucesso"
                            : "mg-badge-alerta"
                        }`}
                      >
                        {c.pendencia}
                      </span>
                    </td>
                    <td style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                      <button
                        className="mg-btn mg-btn-outline"
                        onClick={() => navigate(`/microbiologia/${c.id}/editar`)}
                      >
                        Editar
                      </button>
                      {c.pendencia === "Pronta para liberação" && (
                        <button
                          className="mg-btn mg-btn-secondary"
                          onClick={() => handleLiberar(c)}
                        >
                          Liberar
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <p style={{ marginTop: 14, fontSize: 13, color: "var(--mg-cinza-600)" }}>
              {total} cultura{total !== 1 ? "s" : ""} em andamento
            </p>
          </>
        )}
      </div>
    </MainLayout>
  );
}
