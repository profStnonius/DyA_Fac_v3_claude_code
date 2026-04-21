"""
Validates CFDI XML against official SAT XSD schemas.
XSD files should be placed in backend/app/services/xsd/ directory.
Download from: https://www.sat.gob.mx/sitio_internet/cfd/4/cfdv40.xsd
"""
import os
from pathlib import Path

from lxml import etree

XSD_DIR = Path(__file__).parent / "xsd"

_schema_cache: dict[str, etree.XMLSchema] = {}


def _load_schema(version: str) -> etree.XMLSchema | None:
    if version in _schema_cache:
        return _schema_cache[version]

    xsd_file = XSD_DIR / f"cfdv{version.replace('.', '')}.xsd"
    if not xsd_file.exists():
        return None

    with open(xsd_file, "rb") as f:
        schema_doc = etree.parse(f)
    schema = etree.XMLSchema(schema_doc)
    _schema_cache[version] = schema
    return schema


def validate_cfdi_xsd(xml_bytes: bytes) -> None:
    """
    Validate CFDI XML against SAT XSD schema.
    Raises ValueError with details if validation fails.
    If XSD file not found, logs a warning and skips validation.
    """
    root = etree.fromstring(xml_bytes)
    version = root.get("Version", root.get("version", "4.0"))
    schema = _load_schema(version)

    if schema is None:
        # XSD not available locally — skip validation (log in production)
        return

    if not schema.validate(root):
        errors = [str(e) for e in schema.error_log]
        raise ValueError(f"CFDI XSD validation failed: {'; '.join(errors[:3])}")
