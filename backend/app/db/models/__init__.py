# Import all models so Alembic autogenerate can detect them
from app.db.models.tenant import Tenant, TenantSettings
from app.db.models.user import User, UserTenantRole
from app.db.models.email import EmailAccount, SyncJob, EmailMessage, EmailAttachment
from app.db.models.cfdi import CfdiDocument, CfdiParty, CfdiItem, CfdiTax
from app.db.models.template import ExtractionTemplate
from app.db.models.job import ProcessingJob, BatchDataset
from app.db.models.analytics import AnalyticsSnapshot, ProductsCatalog, ClientsCatalog, SuppliersCatalog
from app.db.models.export import ExportFile, AuditLog

__all__ = [
    "Tenant", "TenantSettings",
    "User", "UserTenantRole",
    "EmailAccount", "SyncJob", "EmailMessage", "EmailAttachment",
    "CfdiDocument", "CfdiParty", "CfdiItem", "CfdiTax",
    "ExtractionTemplate",
    "ProcessingJob", "BatchDataset",
    "AnalyticsSnapshot", "ProductsCatalog", "ClientsCatalog", "SuppliersCatalog",
    "ExportFile", "AuditLog",
]
