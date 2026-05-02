from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from analytics.analytics_schema import (
    AdminOverviewResponse,
    ApplicationsAnalyticsResponse,
    InternshipsAnalyticsResponse,
)
from core.database import get_db
from core.security import require_roles
from models.user_model import User, UserRole
from pydantic import BaseModel
from repositories.analytics_repository import AnalyticsRepository
from repositories.internship_repository import InternshipRepository
from repositories.user_repository import UserRepository
from schemas.admin_schema import AdminCompanyDetailResponse
from schemas.auth_schema import UserResponse
from schemas.internship_schema import InternshipResponse
from services.admin_service import (
    AdminDeleteError,
    AdminInternshipNotFoundError,
    AdminService,
    CompanyApprovalError,
    CompanyNotFoundError,
    UserNotFoundError,
)
from services.analytics_service import AnalyticsService


router = APIRouter(prefix="/admin", tags=["Admin"])


def get_admin_service(db: Session = Depends(get_db)) -> AdminService:
    return AdminService(UserRepository(db), InternshipRepository(db))


def get_analytics_service(db: Session = Depends(get_db)) -> AnalyticsService:
    return AnalyticsService(AnalyticsRepository(db))


@router.patch("/company/{company_id}/approve", response_model=UserResponse)
def approve_company(
    company_id: int,
    service: AdminService = Depends(get_admin_service),
    _: User = Depends(require_roles(UserRole.admin)),
) -> UserResponse:
    try:
        user = service.approve_company(company_id)
    except CompanyNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except CompanyApprovalError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return UserResponse.model_validate(user)


@router.get("/users", response_model=list[UserResponse], status_code=status.HTTP_200_OK)
def list_users(
    service: AdminService = Depends(get_admin_service),
    _: User = Depends(require_roles(UserRole.admin)),
) -> list[UserResponse]:
    users = service.list_users()
    return [UserResponse.model_validate(user) for user in users]


@router.get("/companies", response_model=list[UserResponse], status_code=status.HTTP_200_OK)
def list_companies(
    service: AdminService = Depends(get_admin_service),
    _: User = Depends(require_roles(UserRole.admin)),
) -> list[UserResponse]:
    companies = service.list_companies()
    return [UserResponse.model_validate(company) for company in companies]


@router.get("/company/{company_id}", response_model=AdminCompanyDetailResponse)
def get_company_detail(
    company_id: int,
    service: AdminService = Depends(get_admin_service),
    _: User = Depends(require_roles(UserRole.admin)),
) -> AdminCompanyDetailResponse:
    try:
        company, internships = service.get_company_detail(company_id)
    except CompanyNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except CompanyApprovalError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return AdminCompanyDetailResponse(
        company=UserResponse.model_validate(company),
        internships=[InternshipResponse.model_validate(item) for item in internships],
    )


@router.patch("/users/{user_id}/approve", response_model=UserResponse)
def approve_user(
    user_id: int,
    service: AdminService = Depends(get_admin_service),
    _: User = Depends(require_roles(UserRole.admin)),
) -> UserResponse:
    try:
        user = service.approve_company(user_id)
    except CompanyNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except CompanyApprovalError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return UserResponse.model_validate(user)


class UserStatusUpdate(BaseModel):
    is_active: bool

@router.patch("/users/{user_id}/status", response_model=UserResponse)
def update_user_status(
    user_id: int,
    payload: UserStatusUpdate,
    service: AdminService = Depends(get_admin_service),
    _: User = Depends(require_roles(UserRole.admin)),
) -> UserResponse:
    try:
        user = service.set_user_status(user_id, payload.is_active)
    except UserNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AdminDeleteError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return UserResponse.model_validate(user)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    service: AdminService = Depends(get_admin_service),
    _: User = Depends(require_roles(UserRole.admin)),
) -> Response:
    try:
        service.delete_user(user_id)
    except UserNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AdminDeleteError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/internships",
    response_model=list[InternshipResponse],
    status_code=status.HTTP_200_OK,
)
def list_internships(
    service: AdminService = Depends(get_admin_service),
    _: User = Depends(require_roles(UserRole.admin)),
) -> list[InternshipResponse]:
    internships = service.list_internships()
    return [InternshipResponse.model_validate(item) for item in internships]


@router.delete("/internships/{internship_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_internship(
    internship_id: int,
    service: AdminService = Depends(get_admin_service),
    _: User = Depends(require_roles(UserRole.admin)),
) -> Response:
    try:
        service.delete_internship(internship_id)
    except AdminInternshipNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/analytics/overview",
    response_model=AdminOverviewResponse,
    status_code=status.HTTP_200_OK,
)
def get_admin_overview(
    _: User = Depends(require_roles(UserRole.admin)),
    service: AnalyticsService = Depends(get_analytics_service),
) -> AdminOverviewResponse:
    return service.get_admin_overview()


@router.get(
    "/analytics/applications",
    response_model=ApplicationsAnalyticsResponse,
    status_code=status.HTTP_200_OK,
)
def get_admin_applications_analytics(
    _: User = Depends(require_roles(UserRole.admin)),
    service: AnalyticsService = Depends(get_analytics_service),
) -> ApplicationsAnalyticsResponse:
    return service.get_applications_analytics()


@router.get(
    "/analytics/internships",
    response_model=InternshipsAnalyticsResponse,
    status_code=status.HTTP_200_OK,
)
def get_admin_internships_analytics(
    _: User = Depends(require_roles(UserRole.admin)),
    service: AnalyticsService = Depends(get_analytics_service),
) -> InternshipsAnalyticsResponse:
    return service.get_internships_analytics()
