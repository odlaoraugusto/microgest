import { api, ApiResponse } from "./api";
import { ParametroSistema } from "../types/parametro";

export async function listarParametros(): Promise<ParametroSistema[]> {
  const response = await api.get<ApiResponse<ParametroSistema[]>>(
    "/api/configuracoes/parametros"
  );
  return response.data.data;
}

export async function atualizarParametro(
  chave: string,
  valor: string
): Promise<ParametroSistema> {
  const response = await api.put<ApiResponse<ParametroSistema>>(
    `/api/configuracoes/parametros/${chave}`,
    { valor }
  );
  return response.data.data;
}
