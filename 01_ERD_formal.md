# ERD Formal — CFDI Intelligence Platform

Esquema de 21 tablas. Todas las tablas de negocio incluyen `tenant_id UUID NOT NULL` para aislamiento multi-tenant. PKs son UUID v4 en toda la base.

---

## 1. tenants
| Columna | Tipo | Notas |
|---|---|---|
| id | UUID PK | |
| name | VARCHAR(255) | Razón social |
| rfc | VARCHAR(13) | RFC de la empresa |
| plan | VARCHAR(50) | free / starter / pro / enterprise |
| is_active | BOOLEAN | |
| created_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | |

---

## 2. users
| Columna | Tipo | Notas |
|---|---|---|
| id | UUID PK | |
| email | VARCHAR(255) UNIQUE | |
| full_name | VARCHAR(255) | |
| google_sub | VARCHAR(255) UNIQUE | ID de Google OAuth |
| avatar_url | TEXT | |
| is_active | BOOLEAN | |
| created_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | |

---

## 3. user_tenant_roles
| Columna | Tipo | Notas |
|---|---|---|
| id | UUID PK | |
| user_id | UUID FK → users | |
| tenant_id | UUID FK → tenants | |
| role | VARCHAR(50) | owner / admin / analyst / viewer |
| created_at | TIMESTAMPTZ | |

---

## 4. email_accounts
| Columna | Tipo | Notas |
|---|---|---|
| id | UUID PK | |
| tenant_id | UUID FK → tenants | |
| user_id | UUID FK → users | Usuario que conectó la cuenta |
| email_address | VARCHAR(255) | |
| google_access_token | TEXT | Cifrado en reposo |
| google_refresh_token | TEXT | Cifrado en reposo |
| token_expiry | TIMESTAMPTZ | |
| scopes | TEXT[] | Scopes concedidos |
| is_active | BOOLEAN | |
| last_sync_at | TIMESTAMPTZ | |
| created_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | |

---

## 5. sync_jobs
| Columna | Tipo | Notas |
|---|---|---|
| id | UUID PK | |
| tenant_id | UUID FK → tenants | |
| email_account_id | UUID FK → email_accounts | |
| triggered_by | UUID FK → users | |
| status | VARCHAR(50) | pending / running / completed / failed |
| filter_config | JSONB | Filtros aplicados (remitentes, fechas, etc.) |
| total_messages | INTEGER | |
| processed_messages | INTEGER | |
| failed_messages | INTEGER | |
| started_at | TIMESTAMPTZ | |
| completed_at | TIMESTAMPTZ | |
| error_detail | TEXT | |
| created_at | TIMESTAMPTZ | |

---

## 6. email_messages
| Columna | Tipo | Notas |
|---|---|---|
| id | UUID PK | |
| tenant_id | UUID FK → tenants | |
| email_account_id | UUID FK → email_accounts | |
| sync_job_id | UUID FK → sync_jobs | |
| gmail_message_id | VARCHAR(255) | ID nativo de Gmail |
| thread_id | VARCHAR(255) | |
| from_address | VARCHAR(255) | |
| subject | TEXT | |
| received_at | TIMESTAMPTZ | |
| has_attachments | BOOLEAN | |
| processed | BOOLEAN | |
| created_at | TIMESTAMPTZ | |

---

## 7. email_attachments
| Columna | Tipo | Notas |
|---|---|---|
| id | UUID PK | |
| tenant_id | UUID FK → tenants | |
| email_message_id | UUID FK → email_messages | |
| filename | VARCHAR(500) | |
| content_type | VARCHAR(100) | application/xml, application/pdf, etc. |
| file_size_bytes | INTEGER | |
| storage_path | TEXT | Ruta en object storage |
| storage_bucket | VARCHAR(255) | |
| file_hash | VARCHAR(64) | SHA-256 |
| created_at | TIMESTAMPTZ | |

---

## 8. cfdi_documents
| Columna | Tipo | Notas |
|---|---|---|
| id | UUID PK | |
| tenant_id | UUID FK → tenants | |
| xml_attachment_id | UUID FK → email_attachments | Nullable |
| pdf_attachment_id | UUID FK → email_attachments | Nullable |
| uuid | VARCHAR(36) UNIQUE | UUID fiscal del CFDI |
| version | VARCHAR(10) | 3.3 / 4.0 |
| type | VARCHAR(50) | ingreso / egreso / traslado / nomina / pago |
| direction | VARCHAR(20) | received / issued |
| fecha_emision | TIMESTAMPTZ | |
| fecha_timbrado | TIMESTAMPTZ | |
| moneda | VARCHAR(10) | MXN / USD / etc. |
| tipo_cambio | NUMERIC(18,6) | |
| subtotal | NUMERIC(18,6) | |
| descuento | NUMERIC(18,6) | |
| total_impuestos_trasladados | NUMERIC(18,6) | |
| total_impuestos_retenidos | NUMERIC(18,6) | |
| total | NUMERIC(18,6) | |
| forma_pago | VARCHAR(10) | Catálogo SAT |
| metodo_pago | VARCHAR(10) | PUE / PPD |
| uso_cfdi | VARCHAR(10) | Catálogo SAT |
| lugar_expedicion | VARCHAR(10) | CP |
| serie | VARCHAR(25) | |
| folio | VARCHAR(40) | |
| sello_sat | TEXT | |
| no_certificado_sat | VARCHAR(20) | |
| parse_status | VARCHAR(50) | pending / parsed / error |
| parse_error | TEXT | |
| raw_xml_path | TEXT | Ruta en object storage |
| created_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | |

---

## 9. cfdi_parties (emisor/receptor)
| Columna | Tipo | Notas |
|---|---|---|
| id | UUID PK | |
| tenant_id | UUID FK → tenants | |
| cfdi_document_id | UUID FK → cfdi_documents | |
| party_type | VARCHAR(20) | emisor / receptor |
| rfc | VARCHAR(13) | |
| nombre | VARCHAR(500) | |
| regimen_fiscal | VARCHAR(10) | Catálogo SAT |
| domicilio_fiscal | VARCHAR(10) | CP (CFDI 4.0) |
| created_at | TIMESTAMPTZ | |

---

## 10. cfdi_items (conceptos/partidas)
| Columna | Tipo | Notas |
|---|---|---|
| id | UUID PK | |
| tenant_id | UUID FK → tenants | |
| cfdi_document_id | UUID FK → cfdi_documents | |
| item_index | INTEGER | Orden dentro del CFDI |
| clave_prod_serv | VARCHAR(10) | Catálogo SAT |
| clave_unidad | VARCHAR(10) | |
| no_identificacion | VARCHAR(100) | SKU interno |
| descripcion | TEXT | |
| cantidad | NUMERIC(18,6) | |
| valor_unitario | NUMERIC(18,6) | |
| descuento | NUMERIC(18,6) | |
| importe | NUMERIC(18,6) | |
| objeto_imp | VARCHAR(10) | |
| created_at | TIMESTAMPTZ | |

---

## 11. cfdi_taxes (impuestos por partida o global)
| Columna | Tipo | Notas |
|---|---|---|
| id | UUID PK | |
| tenant_id | UUID FK → tenants | |
| cfdi_document_id | UUID FK → cfdi_documents | |
| cfdi_item_id | UUID FK → cfdi_items | Nullable (impuestos globales) |
| tax_type | VARCHAR(20) | traslado / retencion |
| impuesto | VARCHAR(10) | 001=ISR, 002=IVA, 003=IEPS |
| tipo_factor | VARCHAR(20) | Tasa / Cuota / Exento |
| tasa_cuota | NUMERIC(18,6) | |
| importe | NUMERIC(18,6) | |
| created_at | TIMESTAMPTZ | |

---

## 12. extraction_templates
| Columna | Tipo | Notas |
|---|---|---|
| id | UUID PK | |
| tenant_id | UUID FK → tenants | |
| name | VARCHAR(255) | |
| description | TEXT | |
| version | INTEGER | Versionado de plantillas |
| is_active | BOOLEAN | |
| config | JSONB | Definición completa de campos a extraer |
| created_by | UUID FK → users | |
| created_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | |

Estructura del JSONB `config`:
```json
{
  "source_type": "cfdi",
  "fields": [
    {"key": "fecha", "source": "xml", "path": "Comprobante.Fecha", "type": "date", "required": true},
    {"key": "cliente", "source": "xml", "path": "Receptor.Nombre", "type": "string"},
    {"key": "producto", "source": "xml", "path": "Conceptos[].Descripcion", "type": "string"},
    {"key": "cantidad", "source": "xml", "path": "Conceptos[].Cantidad", "type": "number"},
    {"key": "precio", "source": "xml", "path": "Conceptos[].ValorUnitario", "type": "number"},
    {"key": "total", "source": "xml", "path": "Comprobante.Total", "type": "number"}
  ]
}
```

---

## 13. processing_jobs
| Columna | Tipo | Notas |
|---|---|---|
| id | UUID PK | |
| tenant_id | UUID FK → tenants | |
| triggered_by | UUID FK → users | |
| job_type | VARCHAR(50) | email_sync / cfdi_parse / batch_zip / analytics_refresh / report_export |
| status | VARCHAR(50) | pending / running / completed / failed / cancelled |
| celery_task_id | VARCHAR(255) | |
| input_payload | JSONB | Parámetros del job |
| progress | INTEGER | 0-100 |
| total_items | INTEGER | |
| processed_items | INTEGER | |
| failed_items | INTEGER | |
| output_artifact_id | UUID FK → export_files | Nullable |
| error_detail | TEXT | |
| started_at | TIMESTAMPTZ | |
| completed_at | TIMESTAMPTZ | |
| created_at | TIMESTAMPTZ | |

---

## 14. batch_datasets
| Columna | Tipo | Notas |
|---|---|---|
| id | UUID PK | |
| tenant_id | UUID FK → tenants | |
| processing_job_id | UUID FK → processing_jobs | |
| template_id | UUID FK → extraction_templates | |
| name | VARCHAR(255) | |
| row_count | INTEGER | |
| column_config | JSONB | Columnas generadas |
| storage_path | TEXT | Ruta Excel/CSV en object storage |
| created_at | TIMESTAMPTZ | |

---

## 15. analytics_snapshots
| Columna | Tipo | Notas |
|---|---|---|
| id | UUID PK | |
| tenant_id | UUID FK → tenants | |
| snapshot_type | VARCHAR(50) | monthly_sales / top_products / top_clients / profit_by_product / etc. |
| period_year | INTEGER | |
| period_month | INTEGER | Nullable para snapshots anuales |
| data | JSONB | KPIs calculados |
| computed_at | TIMESTAMPTZ | |
| created_at | TIMESTAMPTZ | |

---

## 16. products_catalog
| Columna | Tipo | Notas |
|---|---|---|
| id | UUID PK | |
| tenant_id | UUID FK → tenants | |
| clave_sat | VARCHAR(10) | |
| descripcion_normalizada | TEXT | Nombre canónico post-normalización |
| alias | TEXT[] | Variantes encontradas |
| cost_reference | NUMERIC(18,6) | Costo de referencia para cálculo de utilidad |
| created_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | |

---

## 17. clients_catalog
| Columna | Tipo | Notas |
|---|---|---|
| id | UUID PK | |
| tenant_id | UUID FK → tenants | |
| rfc | VARCHAR(13) | |
| nombre | VARCHAR(500) | |
| segmento | VARCHAR(100) | |
| created_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | |

---

## 18. suppliers_catalog
| Columna | Tipo | Notas |
|---|---|---|
| id | UUID PK | |
| tenant_id | UUID FK → tenants | |
| rfc | VARCHAR(13) | |
| nombre | VARCHAR(500) | |
| created_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | |

---

## 19. export_files
| Columna | Tipo | Notas |
|---|---|---|
| id | UUID PK | |
| tenant_id | UUID FK → tenants | |
| generated_by | UUID FK → users | |
| export_type | VARCHAR(50) | excel / csv / pdf_report |
| filename | VARCHAR(500) | |
| storage_path | TEXT | |
| storage_bucket | VARCHAR(255) | |
| file_size_bytes | INTEGER | |
| expires_at | TIMESTAMPTZ | Links firmados expiran |
| download_count | INTEGER | |
| created_at | TIMESTAMPTZ | |

---

## 20. audit_logs
| Columna | Tipo | Notas |
|---|---|---|
| id | UUID PK | |
| tenant_id | UUID FK → tenants | |
| user_id | UUID FK → users | Nullable (eventos de sistema) |
| action | VARCHAR(100) | CREATE / UPDATE / DELETE / LOGIN / SYNC / EXPORT / etc. |
| resource_type | VARCHAR(100) | cfdi / template / user / job / etc. |
| resource_id | UUID | |
| old_values | JSONB | |
| new_values | JSONB | |
| ip_address | INET | |
| user_agent | TEXT | |
| created_at | TIMESTAMPTZ | |

---

## 21. tenant_settings
| Columna | Tipo | Notas |
|---|---|---|
| id | UUID PK | |
| tenant_id | UUID FK → tenants UNIQUE | |
| default_template_id | UUID FK → extraction_templates | Nullable |
| gmail_sync_schedule | VARCHAR(50) | cron expression |
| notification_email | VARCHAR(255) | |
| timezone | VARCHAR(50) | America/Mexico_City |
| fiscal_year_start_month | INTEGER | 1 por defecto |
| settings_json | JSONB | Configuración adicional |
| updated_at | TIMESTAMPTZ | |

---

## Índices recomendados

```sql
-- Consultas multi-tenant (en todas las tablas de negocio)
CREATE INDEX idx_cfdi_documents_tenant_id ON cfdi_documents(tenant_id);
CREATE INDEX idx_cfdi_items_tenant_id ON cfdi_items(tenant_id);
CREATE INDEX idx_email_messages_tenant_id ON email_messages(tenant_id);

-- Búsquedas fiscales frecuentes
CREATE INDEX idx_cfdi_documents_uuid ON cfdi_documents(uuid);
CREATE INDEX idx_cfdi_documents_fecha ON cfdi_documents(tenant_id, fecha_emision);
CREATE INDEX idx_cfdi_parties_rfc ON cfdi_parties(tenant_id, rfc);

-- Jobs y estados
CREATE INDEX idx_processing_jobs_status ON processing_jobs(tenant_id, status);
CREATE INDEX idx_sync_jobs_status ON sync_jobs(tenant_id, status);

-- Analytics
CREATE INDEX idx_analytics_snapshots_type_period ON analytics_snapshots(tenant_id, snapshot_type, period_year, period_month);
```
