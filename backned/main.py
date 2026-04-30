from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1.endpoints.admin import router as admin_router
from api.v1.endpoints.analytics import router as analytics_router
from api.v1.endpoints.application import router as application_router
from api.v1.endpoints.auth import router as auth_router
from api.v1.endpoints.certificate import router as certificate_router
from api.v1.endpoints.company import router as company_router
from api.v1.endpoints.internship import router as internship_router
from api.v1.endpoints.progress import router as progress_router
from api.v1.endpoints.recommendation import router as recommendation_router
from api.v1.endpoints.resume import router as resume_router
from api.v1.endpoints.user import router as user_router
from core.config import settings
from core.database import (
    Base,
    SessionLocal,
    engine,
    ensure_application_table_columns,
    ensure_internship_table_columns,
    ensure_user_table_columns,
)
from repositories.user_repository import UserRepository
from services.auth_service import AuthService


@asynccontextmanager
async def lifespan(_: FastAPI):
    # In production, schema changes should be handled with migrations (e.g., Alembic).
    Base.metadata.create_all(bind=engine)
    ensure_user_table_columns(engine)
    ensure_internship_table_columns(engine)
    ensure_application_table_columns(engine)
    if settings.admin_email and settings.admin_password:
        admin_name = settings.admin_name or "Admin"
        with SessionLocal() as session:
            AuthService(UserRepository(session)).ensure_admin_user(
                name=admin_name,
                email=settings.admin_email,
                password=settings.admin_password,
            )
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://internship-recommendation-mu.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(admin_router, prefix=settings.api_v1_prefix)
app.include_router(user_router, prefix=settings.api_v1_prefix)
app.include_router(company_router, prefix=settings.api_v1_prefix)
app.include_router(internship_router, prefix=settings.api_v1_prefix)
app.include_router(application_router, prefix=settings.api_v1_prefix)
app.include_router(progress_router, prefix=settings.api_v1_prefix)
app.include_router(certificate_router, prefix=settings.api_v1_prefix)
app.include_router(analytics_router, prefix=settings.api_v1_prefix)
app.include_router(recommendation_router, prefix=settings.api_v1_prefix)
app.include_router(resume_router, prefix=settings.api_v1_prefix)
