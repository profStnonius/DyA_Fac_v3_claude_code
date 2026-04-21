import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(amount: number | string | null, currency = "MXN"): string {
  if (amount === null || amount === undefined) return "—";
  const num = typeof amount === "string" ? parseFloat(amount) : amount;
  return new Intl.NumberFormat("es-MX", { style: "currency", currency }).format(num);
}

export function formatDate(dateStr: string | null): string {
  if (!dateStr) return "—";
  return new Intl.DateTimeFormat("es-MX", { dateStyle: "medium" }).format(new Date(dateStr));
}

export function formatRfc(rfc: string | null): string {
  return rfc?.toUpperCase() ?? "—";
}
