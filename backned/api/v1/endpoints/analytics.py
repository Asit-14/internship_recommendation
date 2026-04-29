from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from analytics.analytics_schema import (
    ApplicationsAnalyticsResponse,
    DashboardAnalyticsResponse,
    InternshipsAnalyticsResponse,
    UsersAnalyticsResponse,
)
from core.database import get_db
from core.security import require_roles
from models.user_model import User, UserRole
from repositories.analytics_repository import AnalyticsRepository
from services.analytics_service import AnalyticsService


router = APIRouter(prefix="/analytics", tags=["Analytics"])


def get_analytics_service(db: Session = Depends(get_db)) -> AnalyticsService:
    return AnalyticsService(AnalyticsRepository(db))


@router.get("/dashboard", response_model=DashboardAnalyticsResponse, status_code=status.HTTP_200_OK)
def get_dashboard_analytics(
    _: User = Depends(require_roles(UserRole.admin)),
    service: AnalyticsService = Depends(get_analytics_service),
) -> DashboardAnalyticsResponse:
    return service.get_dashboard_analytics()


@router.get("/users", response_model=UsersAnalyticsResponse, status_code=status.HTTP_200_OK)
def get_users_analytics(
    _: User = Depends(require_roles(UserRole.admin)),
    service: AnalyticsService = Depends(get_analytics_service),
) -> UsersAnalyticsResponse:
    return service.get_users_analytics()


@router.get("/internships", response_model=InternshipsAnalyticsResponse, status_code=status.HTTP_200_OK)
def get_internships_analytics(
    _: User = Depends(require_roles(UserRole.admin)),
    service: AnalyticsService = Depends(get_analytics_service),
) -> InternshipsAnalyticsResponse:
    return service.get_internships_analytics()


@router.get("/applications", response_model=ApplicationsAnalyticsResponse, status_code=status.HTTP_200_OK)
def get_applications_analytics(
    _: User = Depends(require_roles(UserRole.admin)),
    service: AnalyticsService = Depends(get_analytics_service),
) -> ApplicationsAnalyticsResponse:
    return service.get_applications_analytics()
