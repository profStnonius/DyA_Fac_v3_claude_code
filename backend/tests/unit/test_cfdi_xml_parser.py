"""Unit tests for the CFDI XML parser."""
import pytest
import uuid
from decimal import Decimal

from app.services.cfdi_xml_parser import parse_cfdi_xml_bytes

SAMPLE_CFDI_40 = b"""<?xml version="1.0" encoding="UTF-8"?>
<cfdi:Comprobante
  xmlns:cfdi="http://www.sat.gob.mx/cfd/4"
  xmlns:tfd="http://www.sat.gob.mx/TimbreFiscalDigital"
  Version="4.0"
  Serie="A"
  Folio="123"
  Fecha="2024-01-15T12:00:00"
  SubTotal="1000.00"
  Total="1160.00"
  Descuento="0.00"
  Moneda="MXN"
  TipoCambio="1"
  TipoDeComprobante="I"
  MetodoPago="PUE"
  FormaPago="03"
  LugarExpedicion="64000"
  Certificado=""
  NoCertificado="123"
  Sello="">
  <cfdi:Emisor Rfc="AAA010101AAA" Nombre="Empresa Emisora SA" RegimenFiscal="601"/>
  <cfdi:Receptor Rfc="BBB020202BBB" Nombre="Empresa Receptora SA" UsoCFDI="G03"
    DomicilioFiscalReceptor="01000" RegimenFiscalReceptor="601"/>
  <cfdi:Conceptos>
    <cfdi:Concepto ClaveProdServ="01010101" ClaveUnidad="H87"
      Descripcion="Producto A" Cantidad="2" ValorUnitario="500.00"
      Importe="1000.00" ObjetoImp="02">
      <cfdi:Impuestos>
        <cfdi:Traslados>
          <cfdi:Traslado Base="1000.00" Impuesto="002" TipoFactor="Tasa"
            TasaOCuota="0.160000" Importe="160.00"/>
        </cfdi:Traslados>
      </cfdi:Impuestos>
    </cfdi:Concepto>
  </cfdi:Conceptos>
  <cfdi:Impuestos TotalImpuestosTrasladados="160.00">
    <cfdi:Traslados>
      <cfdi:Traslado Base="1000.00" Impuesto="002" TipoFactor="Tasa"
        TasaOCuota="0.160000" Importe="160.00"/>
    </cfdi:Traslados>
  </cfdi:Impuestos>
  <cfdi:Complemento>
    <tfd:TimbreFiscalDigital
      xmlns:tfd="http://www.sat.gob.mx/TimbreFiscalDigital"
      UUID="6128396f-c09b-4ec6-8699-43c5f7e3b230"
      NoCertificadoSAT="20001000000300022816"
      SelloSAT="abc123"/>
  </cfdi:Complemento>
</cfdi:Comprobante>"""


def test_parse_cfdi_40_extracts_uuid():
    tenant_id = uuid.uuid4()
    result = parse_cfdi_xml_bytes(SAMPLE_CFDI_40, tenant_id)
    assert result["document"]["uuid"] == "6128396f-c09b-4ec6-8699-43c5f7e3b230"


def test_parse_cfdi_40_extracts_totals():
    tenant_id = uuid.uuid4()
    result = parse_cfdi_xml_bytes(SAMPLE_CFDI_40, tenant_id)
    assert result["document"]["total"] == Decimal("1160.00")
    assert result["document"]["subtotal"] == Decimal("1000.00")


def test_parse_cfdi_40_extracts_parties():
    tenant_id = uuid.uuid4()
    result = parse_cfdi_xml_bytes(SAMPLE_CFDI_40, tenant_id)
    parties = result["parties"]
    assert len(parties) == 2
    emisor = next(p for p in parties if p["party_type"] == "emisor")
    assert emisor["rfc"] == "AAA010101AAA"


def test_parse_cfdi_40_extracts_items():
    tenant_id = uuid.uuid4()
    result = parse_cfdi_xml_bytes(SAMPLE_CFDI_40, tenant_id)
    items = result["items"]
    assert len(items) == 1
    assert items[0]["descripcion"] == "Producto A"
    assert items[0]["cantidad"] == Decimal("2")
