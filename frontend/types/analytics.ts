export interface KpiSummary {
  totalCfdiCount: number;
  totalSalesAmount: number;
  totalPurchasesAmount: number;
  estimatedProfit: number;
  currency: string;
}

export interface TopProduct {
  descripcion: string;
  claveProdServ: string | null;
  totalAmount: number;
  totalQuantity: number;
  rank: number;
}

export interface TopClient {
  rfc: string;
  nombre: string;
  totalAmount: number;
  cfdiCount: number;
  rank: number;
}

export interface MonthlySales {
  year: number;
  month: number;
  salesAmount: number;
  purchasesAmount: number;
  cfdiCount: number;
}
