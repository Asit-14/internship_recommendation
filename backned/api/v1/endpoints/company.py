from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from core.config import settings
from core.database import get_db
from core.security import require_roles
from models.user_model import User, UserRole
from repositories.application_repository import ApplicationRepository
from repositories.internship_repository import InternshipRepository
from schemas.application_schema import ApplicantProfileResponse, ApplicantSummaryResponse
from schemas.internship_schema import InternshipResponse
from services.application_service import (
    ApplicationService,
    ForbiddenApplicationAccessError,
    InternshipNotFoundError,
)
from services.internship_service import InternshipService


router = APIRouter(prefix="/company", tags=["Company"])


def get_internship_service(db: Session = Depends(get_db)) -> InternshipService:
    return InternshipService(InternshipRepository(db))


def get_application_service(db: Session = Depends(get_db)) -> ApplicationService:
    return ApplicationService(ApplicationRepository(db))


def _build_resume_url(application_id: int, resume_key: str | None) -> str | None:
    if not resume_key:
        return None

    return f"{settings.api_v1_prefix}/applications/{application_id}/resume"


@router.get("/internships", response_model=list[InternshipResponse], status_code=status.HTTP_200_OK)
def get_company_internships(
    current_user: User = Depends(require_roles(UserRole.company)),
    service: InternshipService = Depends(get_internship_service),
) -> list[InternshipResponse]:
    return service.get_company_internships(current_user.id)


@router.get(
    "/internships/{internship_id}/applicants",
    response_model=list[ApplicantSummaryResponse],
    status_code=status.HTTP_200_OK,
)
def get_internship_applicants(
    internship_id: int = Path(gt=0),
    current_user: User = Depends(require_roles(UserRole.company, UserRole.admin)),
    service: ApplicationService = Depends(get_application_service),
) -> list[ApplicantSummaryResponse]:
    try:
        applicants = service.get_company_applicants(internship_id, current_user)
    except InternshipNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ForbiddenApplicationAccessError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    responses: list[ApplicantSummaryResponse] = []
    for application, student in applicants:
        resume_url = _build_resume_url(application.id, application.resume_url)
        student_profile = ApplicantProfileResponse.model_validate(student).model_copy(
            update={"resume_url": resume_url}
        )
        responses.append(
            ApplicantSummaryResponse(
                application_id=application.id,
                internship_id=application.internship_id,
                status=application.status,
                applied_at=application.applied_at,
                resume_url=resume_url,
                student=student_profile,
            )
        )

    return responses
