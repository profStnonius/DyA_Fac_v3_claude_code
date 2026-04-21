export interface TemplateField {
  key: string;
  source: "xml" | "pdf";
  path: string;
  type: "string" | "number" | "date" | "boolean";
  required: boolean;
  nullable: boolean;
  format: string | null;
}

export interface ExtractionTemplate {
  id: string;
  name: string;
  description: string | null;
  version: number;
  isActive: boolean;
  config: { source_type: string; fields: TemplateField[] };
  createdAt: string;
}
