from fastapi import APIRouter

from app.api.v1 import auth, tenants, users, gmail, cfdi, templates, batch, jobs, analytics, exports

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(tenants.router, prefix="/tenants", tags=["tenants"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(gmail.router, prefix="/gmail", tags=["gmail"])
api_router.include_router(cfdi.router, prefix="/cfdi", tags=["cfdi"])
api_router.include_router(templates.router, prefix="/templates", tags=["templates"])
api_router.include_router(batch.router, prefix="/batch", tags=["batch"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(exports.router, prefix="/exports", tags=["exports"])
