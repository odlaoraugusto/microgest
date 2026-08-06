import { api, ApiResponse } from "./api";
import { IndicadoresCCIH } from "../types/ccih";

export async function obterIndicadoresCCIH(
  dataInicio?: string,
  dataFim?: string,
  origem?: string
): Promise<IndicadoresCCIH> {
  const response = await api.get<ApiResponse<IndicadoresCCIH>>("/api/ccih/indicadores", {
    params: { data_inicio: dataInicio, data_fim: dataFim, origem: origem || undefined },
  });
  return response.data.data;
}

export async function obterIndicadoresCCIHVigilancia(
  dataInicio?: string,
  dataFim?: string,
  origem?: string
): Promise<IndicadoresCCIH> {
  const response = await api.get<ApiResponse<IndicadoresCCIH>>(
    "/api/ccih/indicadores/vigilancia",
    { params: { data_inicio: dataInicio, data_fim: dataFim, origem: origem || undefined } }
  );
  return response.data.data;
}
