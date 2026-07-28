import { useEffect, useState } from "react";
import MainLayout from "../layouts/MainLayout";
import { api, extrairMensagemErro } from "../services/api";
import { listarSetores } from "../services/setorService";

function hojeISO() {
  return new Date().toISOString().slice(0, 10);
}

function primeiroDiaDoMesISO() {
  const agora = new Date();
  return new Date(agora.getFullYear(), agora.getMonth(), 1).toISOString().slice(0, 10);
}

/**
 * Baixa um arquivo autenticado da API.
 *
 * Os relatórios exigem login (o backend trava esses endpoints), então não
 * dá pra usar um simples `<a href>` - navegação de link não carrega o
 * header Authorization. Por isso o download é feito via axios (que já
 * anexa o token automaticamente) e o arquivo é entregue como Blob.
 */
async function baixarArquivo(
  caminho: string,
  nomeArquivo: string,
  params?: Record<string, string>
) {
  const response = await api.get(caminho, { params, responseType: "blob" });
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement("a");
  link.href = url;
  link.download = nomeArquivo;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}

interface RelatorioCardProps {
  titulo: string;
  descricao: string;
  botaoLabel: string;
  onBaixar: () => Promise<void>;
}

function RelatorioCard({ titulo, descricao, botaoLabel, onBaixar }: RelatorioCardProps) {
  const [baixando, setBaixando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);

  async function handleClick() {
    setBaixando(true);
    setErro(null);
    try {
      await onBaixar();
    } catch (err: unknown) {
      setErro(extrairMensagemErro(err, "Não foi possível baixar o relatório."));
    } finally {
      setBaixando(false);
    }
  }

  return (
    <div className="mg-card" style={{ flex: 1, minWidth: 280 }}>
      <h3 style={{ marginTop: 0 }}>{titulo}</h3>
      <p style={{ color: "var(--mg-cinza-600)", fontSize: 14, minHeight: 40 }}>{descricao}</p>
      {erro && <p style={{ color: "var(--mg-erro)", fontSize: 13 }}>{erro}</p>}
      <button className="mg-btn mg-btn-primary" onClick={handleClick} disabled={baixando}>
        {baixando ? "Baixando..." : botaoLabel}
      </button>
    </div>
  );
}

export default function RelatoriosPage() {
  const [dataInicio, setDataInicio] = useState(primeiroDiaDoMesISO());
  const [dataFim, setDataFim] = useState(hojeISO());
  const [setor, setSetor] = useState("");
  const [setoresCatalogo, setSetoresCatalogo] = useState<string[]>([]);
  const [baixandoCcih, setBaixandoCcih] = useState(false);
  const [erroCcih, setErroCcih] = useState<string | null>(null);

  useEffect(() => {
    listarSetores().then((res) => setSetoresCatalogo(res.items.map((s) => s.nome)));
  }, []);

  async function handleBaixarCcih() {
    setBaixandoCcih(true);
    setErroCcih(null);
    try {
      const params: Record<string, string> = { data_inicio: dataInicio, data_fim: dataFim };
      if (setor) params.origem = setor;
      await baixarArquivo("/api/relatorios/ccih.pdf", "microgest_relatorio_ccih.pdf", params);
    } catch (err: unknown) {
      setErroCcih(extrairMensagemErro(err, "Não foi possível baixar o relatório."));
    } finally {
      setBaixandoCcih(false);
    }
  }

  return (
    <MainLayout titulo="Relatórios" subtitulo="Exportação de dados e relatório da CCIH">
      <div style={{ display: "flex", gap: 16, flexWrap: "wrap", marginBottom: 20 }}>
        <RelatorioCard
          titulo="Pacientes (Excel)"
          descricao="Exporta a lista completa de pacientes cadastrados, com setor, leito e status de internação."
          botaoLabel="Baixar .xlsx"
          onBaixar={() =>
            baixarArquivo("/api/relatorios/pacientes.xlsx", "microgest_pacientes.xlsx")
          }
        />
        <RelatorioCard
          titulo="Solicitações (Excel)"
          descricao="Exporta todas as solicitações registradas, com material, origem, prioridade e status."
          botaoLabel="Baixar .xlsx"
          onBaixar={() =>
            baixarArquivo("/api/relatorios/solicitacoes.xlsx", "microgest_solicitacoes.xlsx")
          }
        />
        <RelatorioCard
          titulo="Resultados Parciais (Excel)"
          descricao="Culturas ainda em andamento (não liberadas), com previsão de liberação e o que está pendente em cada uma."
          botaoLabel="Baixar .xlsx"
          onBaixar={() =>
            baixarArquivo(
              "/api/relatorios/culturas-parciais.xlsx",
              "microgest_resultados_parciais.xlsx"
            )
          }
        />
      </div>

      <div className="mg-card" style={{ maxWidth: 520 }}>
        <h3 style={{ marginTop: 0 }}>Relatório CCIH (PDF)</h3>
        <p style={{ color: "var(--mg-cinza-600)", fontSize: 14 }}>
          Relatório consolidado pronto para a reunião da CCIH: resumo geral, distribuição por
          setor, perfil microbiológico e mapa de resistência do período selecionado.
        </p>

        <div className="mg-form-grid" style={{ marginBottom: 16 }}>
          <div className="mg-field">
            <label>De</label>
            <input type="date" value={dataInicio} onChange={(e) => setDataInicio(e.target.value)} />
          </div>
          <div className="mg-field">
            <label>Até</label>
            <input type="date" value={dataFim} onChange={(e) => setDataFim(e.target.value)} />
          </div>
          <div className="mg-field" style={{ gridColumn: "1 / -1" }}>
            <label>Setor</label>
            <select value={setor} onChange={(e) => setSetor(e.target.value)}>
              <option value="">Todos os setores</option>
              {setoresCatalogo.map((nome) => (
                <option key={nome} value={nome}>
                  {nome}
                </option>
              ))}
            </select>
          </div>
        </div>

        {erroCcih && <p style={{ color: "var(--mg-erro)", fontSize: 13 }}>{erroCcih}</p>}
        <button className="mg-btn mg-btn-primary" onClick={handleBaixarCcih} disabled={baixandoCcih}>
          {baixandoCcih ? "Baixando..." : "Baixar relatório .pdf"}
        </button>
      </div>
    </MainLayout>
  );
}
