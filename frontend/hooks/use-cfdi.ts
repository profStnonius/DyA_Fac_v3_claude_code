import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import type { CfdiListResponse, CfdiDocumentDetail } from "@/types/cfdi";

export function useCfdiList(params: {
  page?: number;
  pageSize?: number;
  direction?: string;
  rfc?: string;
}) {
  return useQuery({
    queryKey: ["cfdi", "list", params],
    queryFn: async () => {
      const res = await apiClient.get<CfdiListResponse>("/api/v1/cfdi/", { params });
      return res.data;
    },
  });
}

export function useCfdiDetail(cfdiId: string) {
  return useQuery({
    queryKey: ["cfdi", "detail", cfdiId],
    queryFn: async () => {
      const res = await apiClient.get<CfdiDocumentDetail>(`/api/v1/cfdi/${cfdiId}`);
      return res.data;
    },
    enabled: !!cfdiId,
  });
}
