import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import type { ProcessingJob } from "@/types/job";

export function useJob(jobId: string, refetchWhileRunning = true) {
  return useQuery({
    queryKey: ["jobs", jobId],
    queryFn: async () => {
      const res = await apiClient.get<ProcessingJob>(`/api/v1/jobs/${jobId}`);
      return res.data;
    },
    enabled: !!jobId,
    refetchInterval: (query) => {
      if (!refetchWhileRunning) return false;
      const status = query.state.data?.status;
      return status === "pending" || status === "running" ? 3000 : false;
    },
  });
}
