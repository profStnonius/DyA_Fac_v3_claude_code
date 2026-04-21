export type JobType = "email_sync" | "cfdi_parse" | "batch_zip" | "analytics_refresh" | "report_export";
export type JobStatus = "pending" | "running" | "completed" | "failed" | "cancelled";

export interface ProcessingJob {
  id: string;
  jobType: JobType;
  status: JobStatus;
  progress: number;
  totalItems: number | null;
  processedItems: number;
  failedItems: number;
  outputArtifactId: string | null;
  errorDetail: string | null;
  startedAt: string | null;
  completedAt: string | null;
  createdAt: string;
}
