export interface CfdiDocument {
  id: string;
  uuid: string;
  version: string | null;
  type: string | null;
  direction: "received" | "issued" | null;
  fechaEmision: string | null;
  moneda: string | null;
  subtotal: string | null;
  total: string | null;
  parseStatus: "pending" | "parsed" | "error";
}

export interface CfdiParty {
  partyType: "emisor" | "receptor";
  rfc: string | null;
  nombre: string | null;
  regimenFiscal: string | null;
}

export interface CfdiItem {
  itemIndex: number;
  claveProdServ: string | null;
  noIdentificacion: string | null;
  descripcion: string | null;
  cantidad: string | null;
  valorUnitario: string | null;
  descuento: string | null;
  importe: string | null;
}

export interface CfdiDocumentDetail extends CfdiDocument {
  parties: CfdiParty[];
  items: CfdiItem[];
}

export interface CfdiListResponse {
  items: CfdiDocument[];
  total: number;
  page: number;
  pageSize: number;
}
