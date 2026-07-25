import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import MainLayout from "../layouts/MainLayout";
import ResultadoSIRBadge from "../components/ResultadoSIRBadge";
import {
  liberarAntibiograma,
  listarAntibiogramas,
  removerAntibiograma,
} from "../services/antibiogramaService";
import { extrairMensagemErro } from "../services/api";
import { Antibiograma } from "../types/antibiograma";

export default function AntibiogramasPage() {
  const navigate = useNavigate();
  const [antibiogramas, setAntibiogramas] = useState<Antibiograma[]>([]);
  const [total, setTotal] = useState(0);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);

  async function carregar() {
    setCarregando(true);
    setErro(null);
    try {
      const resultado = await listarAntibiogramas();
      setAntibiogramas(resultado.items);
      setTotal(resultado.total);
    } catch {
      setErro(
        "Não foi possível carregar os antibiogramas. Verifique se a API está rodando em " +
          "http://localhost:8000."
      );
    } finally {
      setCarregando(false);
    }
  }

  // Carrega a lista de antibiogramas uma vez, na montagem da página.
  useEffect(() => {
    carregar();
  }, []);

  async function handleLiberar(antibiograma: Antibiograma) {
    try {
      await liberarAntibiograma(antibiograma.id);
      carregar();
    } catch (err: unknown) {
      window.alert(extrairMensagemErro(err, "Não foi possível liberar o antibiograma."));
    }
  }

  async function handleRemover(antibiograma: Antibiograma) {
    const confirmar = window.confirm("Remover este antibiograma?");
    if (!confirmar) return;
    await removerAntibiograma(antibiograma.id);
    carregar();
  }

  return (
    <MainLayout titulo="Antibiogramas" subtitulo="Perfis de sensibilidade e resistência">
      <div className="mg-page-header">
        <div />
        <button className="mg-btn mg-btn-primary" onClick={() => navigate("/antibiogramas/novo")}>
          + Novo Antibiograma
        </button>
      </div>

      <div className="mg-card">
        {erro && <p style={{ color: "var(--mg-erro)", fontSize: 14 }}>{erro}</p>}

        {!erro && carregando && <p style={{ color: "var(--mg-cinza-600)" }}>Carregando...</p>}

        {!erro && !carregando && antibiogramas.length === 0 && (
          <p style={{ color: "var(--mg-cinza-600)" }}>Nenhum antibiograma cadastrado.</p>
        )}

        {!erro && !carregando && antibiogramas.length > 0 && (
          <>
            {antibiogramas.map((a) => (
              <div
                key={a.id}
                className="mg-card"
                style={{ marginBottom: 14, border: "1px solid var(--mg-cinza-200)" }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                  <div>
                    <h4 style={{ margin: "0 0 4px 0" }}>
                      {a.cultura_microrganismo?.microrganismo.nome ?? "Microrganismo"}
                    </h4>
                    <span
                      className={`mg-badge ${a.data_liberacao ? "mg-badge-sucesso" : "mg-badge-alerta"}`}
                    >
                      {a.data_liberacao ? "Liberado" : "Não liberado"}
                    </span>
                  </div>
                  <div style={{ display: "flex", gap: 8 }}>
                    <button
                      className="mg-btn mg-btn-outline"
                      onClick={() => navigate(`/antibiogramas/${a.id}/editar`)}
                    >
                      Editar
                    </button>
                    {!a.data_liberacao && (
                      <button className="mg-btn mg-btn-secondary" onClick={() => handleLiberar(a)}>
                        Liberar
                      </button>
                    )}
                    <button
                      className="mg-btn mg-btn-outline"
                      style={{ color: "var(--mg-erro)" }}
                      onClick={() => handleRemover(a)}
                    >
                      Remover
                    </button>
                  </div>
                </div>

                <div style={{ display: "flex", flexWrap: "wrap", gap: 10, marginTop: 12 }}>
                  {a.resultados.map((r) => (
                    <div
                      key={r.antimicrobiano.id}
                      style={{ display: "flex", alignItems: "center", gap: 6 }}
                    >
                      <span style={{ fontSize: 13 }}>{r.antimicrobiano.nome}</span>
                      <ResultadoSIRBadge resultado={r.resultado} />
                    </div>
                  ))}
                  {a.resultados.length === 0 && (
                    <span style={{ fontSize: 13, color: "var(--mg-cinza-600)" }}>
                      Nenhum resultado adicionado ainda.
                    </span>
                  )}
                </div>
              </div>
            ))}
            <p style={{ fontSize: 13, color: "var(--mg-cinza-600)" }}>
              {total} antibiograma{total !== 1 ? "s" : ""} encontrado{total !== 1 ? "s" : ""}
            </p>
          </>
        )}
      </div>
    </MainLayout>
  );
}
