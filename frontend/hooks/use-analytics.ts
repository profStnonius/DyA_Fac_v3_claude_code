import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import type { KpiSummary, TopProduct, TopClient, MonthlySales } from "@/types/analytics";

export function useKpiSummary(year?: number, month?: number) {
  return useQuery({
    queryKey: ["analytics", "summary", year, month],
    queryFn: async () => {
      const res = await apiClient.get<KpiSummary>("/api/v1/analytics/kpis/summary", {
        params: { year, month },
      });
      return res.data;
    },
  });
}

export function useTopProducts(year?: number, limit = 10) {
  return useQuery({
    queryKey: ["analytics", "top-products", year, limit],
    queryFn: async () => {
      const res = await apiClient.get<TopProduct[]>("/api/v1/analytics/kpis/top-products", {
        params: { year, limit },
      });
      return res.data;
    },
  });
}

export function useTopClients(year?: number, limit = 10) {
  return useQuery({
    queryKey: ["analytics", "top-clients", year, limit],
    queryFn: async () => {
      const res = await apiClient.get<TopClient[]>("/api/v1/analytics/kpis/top-clients", {
        params: { year, limit },
      });
      return res.data;
    },
  });
}

export function useSalesByMonth(year?: number) {
  return useQuery({
    queryKey: ["analytics", "sales-by-month", year],
    queryFn: async () => {
      const res = await apiClient.get<MonthlySales[]>("/api/v1/analytics/kpis/sales-by-month", {
        params: { year },
      });
      return res.data;
    },
  });
}
