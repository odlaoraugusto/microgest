import { api, ApiResponse } from "./api";
import { IndicadoresCCIH } from "../types/ccih";

export async function obterIndicadoresCCIH(
  dataInicio?: string,
  dataFim?: string
): Promise<IndicadoresCCIH> {
  const response = await api.get<ApiResponse<IndicadoresCCIH>>("/api/ccih/indicadores", {
    params: { data_inicio: dataInicio, data_fim: dataFim },
  });
  return response.data.data;
}
