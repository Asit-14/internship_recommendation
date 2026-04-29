from fastapi import APIRouter, Depends, HTTPException, Path, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from core.config import settings
from core.database import get_db
from core.security import get_current_user, require_role, require_roles
from models.user_model import User, UserRole
from repositories.application_repository import ApplicationRepository
from schemas.application_schema import (
    ApplicantProfileResponse,
    ApplicationCreateRequest,
    ApplicationDetailResponse,
    ApplicationResponse,
    ApplicationStatusUpdateRequest,
)
from services.application_service import (
    ApplicationAlreadyExistsError,
    ApplicationNotFoundError,
    ApplicationService,
    ForbiddenApplicationAccessError,
    InternshipNotFoundError,
    InvalidStatusTransitionError,
    MissingResumeError,
    ResumeNotFoundError,
)


router = APIRouter(prefix="/applications", tags=["Applications"])


def get_application_service(db: Session = Depends(get_db)) -> ApplicationService:
    return ApplicationService(ApplicationRepository(db))


def _build_resume_url(application_id: int, resume_key: str | None) -> str | None:
    if not resume_key:
        return None

    return f"{settings.api_v1_prefix}/applications/{application_id}/resume"


@router.post("/", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def apply_to_internship(
    payload: ApplicationCreateRequest,
    current_user: User = Depends(require_role(UserRole.student)),
    service: ApplicationService = Depends(get_application_service),
) -> ApplicationResponse:
    try:
        application = service.apply(payload, current_user)
    except InternshipNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ApplicationAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except MissingResumeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    response = ApplicationResponse.model_validate(application)
    return response.model_copy(
        update={
            "resume_url": _build_resume_url(application.id, application.resume_url),
        }
    )


@router.get("/my", response_model=list[ApplicationResponse], status_code=status.HTTP_200_OK)
def get_my_applications(
    current_user: User = Depends(require_role(UserRole.student)),
    service: ApplicationService = Depends(get_application_service),
) -> list[ApplicationResponse]:
    applications = service.get_my_applications_with_internship(current_user)
    responses: list[ApplicationResponse] = []

    for application, internship in applications:
        response = ApplicationResponse.model_validate(application)
        responses.append(
            response.model_copy(
                update={
                    "internship_title": internship.title,
                    "company_name": internship.company_name,
                    "resume_url": _build_resume_url(application.id, application.resume_url),
                }
            )
        )

    return responses


@router.get(
    "/{application_id}",
    response_model=ApplicationDetailResponse,
    status_code=status.HTTP_200_OK,
)
def get_application_details(
    application_id: int = Path(gt=0),
    current_user: User = Depends(get_current_user),
    service: ApplicationService = Depends(get_application_service),
) -> ApplicationDetailResponse:
    try:
        application, student, internship = service.get_application_detail(
            application_id,
            current_user,
        )
    except ApplicationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ForbiddenApplicationAccessError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    resume_url = _build_resume_url(application.id, application.resume_url)
    student_profile = ApplicantProfileResponse.model_validate(student).model_copy(
        update={"resume_url": resume_url}
    )

    return ApplicationDetailResponse(
        id=application.id,
        internship_id=application.internship_id,
        status=application.status,
        applied_at=application.applied_at,
        updated_at=application.updated_at,
        resume_url=resume_url,
        internship_title=internship.title,
        company_name=internship.company_name,
        student=student_profile,
    )


@router.patch(
    "/{application_id}/status",
    response_model=ApplicationResponse,
    status_code=status.HTTP_200_OK,
)
def update_application_status(
    payload: ApplicationStatusUpdateRequest,
    application_id: int = Path(gt=0),
    current_user: User = Depends(require_roles(UserRole.company, UserRole.admin)),
    service: ApplicationService = Depends(get_application_service),
) -> ApplicationResponse:
    try:
        application = service.update_application_status(
            application_id,
            payload.status,
            current_user,
        )
    except ApplicationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except InvalidStatusTransitionError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ForbiddenApplicationAccessError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    response = ApplicationResponse.model_validate(application)
    return response.model_copy(
        update={
            "resume_url": _build_resume_url(application.id, application.resume_url),
        }
    )


@router.get(
    "/{application_id}/resume",
    status_code=status.HTTP_200_OK,
)
def download_application_resume(
    application_id: int = Path(gt=0),
    current_user: User = Depends(get_current_user),
    service: ApplicationService = Depends(get_application_service),
) -> FileResponse:
    try:
        resume_path = service.get_application_resume_path(application_id, current_user)
    except ApplicationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ForbiddenApplicationAccessError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ResumeNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return FileResponse(
        path=resume_path,
        filename=resume_path.name,
        media_type="application/octet-stream",
    )