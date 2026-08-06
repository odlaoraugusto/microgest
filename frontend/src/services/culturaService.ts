import { api, ApiResponse } from "./api";
import {
  Cultura,
  CulturaFormData,
  CulturaListagem,
  CulturaMicrorganismo,
  CulturaParcialListagem,
} from "../types/cultura";

export async function listarCulturas(
  solicitacaoId?: string,
  page = 1,
  pageSize = 20
): Promise<CulturaListagem> {
  const response = await api.get<ApiResponse<CulturaListagem>>(
    "/api/microbiologia/culturas",
    { params: { solicitacao_id: solicitacaoId, page, page_size: pageSize } }
  );
  return response.data.data;
}

export async function listarResultadosParciais(): Promise<CulturaParcialListagem> {
  const response = await api.get<ApiResponse<CulturaParcialListagem>>(
    "/api/microbiologia/culturas/parciais"
  );
  return response.data.data;
}

export async function obterCultura(id: string): Promise<Cultura> {
  const response = await api.get<ApiResponse<Cultura>>(
    `/api/microbiologia/culturas/${id}`
  );
  return response.data.data;
}

export async function criarCultura(dados: CulturaFormData): Promise<Cultura> {
  const response = await api.post<ApiResponse<Cultura>>(
    "/api/microbiologia/culturas",
    dados
  );
  return response.data.data;
}

export async function atualizarCultura(
  id: string,
  dados: Partial<CulturaFormData>
): Promise<Cultura> {
  const response = await api.put<ApiResponse<Cultura>>(
    `/api/microbiologia/culturas/${id}`,
    dados
  );
  return response.data.data;
}

export async function liberarCultura(id: string): Promise<Cultura> {
  const response = await api.post<ApiResponse<Cultura>>(
    `/api/microbiologia/culturas/${id}/liberar`
  );
  return response.data.data;
}

export async function removerCultura(id: string): Promise<void> {
  await api.delete(`/api/microbiologia/culturas/${id}`);
}

export async function marcarIsoladoSemAntibiograma(
  isoladoId: string,
  valor: boolean
): Promise<CulturaMicrorganismo> {
  const response = await api.put<ApiResponse<CulturaMicrorganismo>>(
    `/api/microbiologia/isolados/${isoladoId}/sem-antibiograma`,
    { sem_antibiograma_padronizado: valor }
  );
  return response.data.data;
}
