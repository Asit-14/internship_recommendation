from fastapi import APIRouter, Depends, HTTPException, status, Path
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_current_user, require_roles
from models.user_model import User, UserRole
from schemas.application_schema import ApplicationStatusEnum
from repositories.certificate_repository import CertificateRepository
from schemas.certificate_schema import CertificateGenerateRequest, CertificateResponse
from services.certificate_service import (
    CertificateConflictError,
    CertificateNotFoundError,
    CertificatePermissionDeniedError,
    CertificateService,
    CertificateValidationError,
)
from services.application_service import ApplicationService, ForbiddenApplicationAccessError
from repositories.application_repository import ApplicationRepository


router = APIRouter(prefix="/certificate", tags=["Certificates"])


def get_certificate_service(db: Session = Depends(get_db)) -> CertificateService:
    return CertificateService(CertificateRepository(db))


@router.post("/{application_id}/generate-missing", response_model=CertificateResponse)
def generate_missing_certificate(
    application_id: int = Path(gt=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    service: CertificateService = Depends(get_certificate_service),
):
    app_service = ApplicationService(ApplicationRepository(db))
    try:
        application, student, internship = app_service.get_application_detail(application_id, current_user)
        
        if application.status != ApplicationStatusEnum.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Internship must be marked as COMPLETED to generate a certificate"
            )
            
        return service.generate_certificate(
            CertificateGenerateRequest(application_id=application_id),
            generated_by=current_user
        )
    except ForbiddenApplicationAccessError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except CertificatePermissionDeniedError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except CertificateValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except CertificateConflictError:
        # If it already exists, just return it
        return service.certificate_repository.get_by_user_and_internship(
            user_id=application.user_id,
            internship_id=application.internship_id
        )
    except Exception as e:
        # Log the error for debugging
        print(f"Error in generate_missing_certificate: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/generate", response_model=CertificateResponse, status_code=status.HTTP_201_CREATED)
def generate_certificate(
    payload: CertificateGenerateRequest,
    service: CertificateService = Depends(get_certificate_service),
    current_user: User = Depends(require_roles(UserRole.admin)),
) -> CertificateResponse:
    try:
        return service.generate_certificate(payload, generated_by=current_user)
    except CertificateNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except CertificatePermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except CertificateConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except CertificateValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/my", response_model=list[CertificateResponse])
def get_my_certificates(
    service: CertificateService = Depends(get_certificate_service),
    current_user: User = Depends(get_current_user),
) -> list[CertificateResponse]:
    return service.get_my_certificates(current_user=current_user)


@router.get("/{id}", response_class=FileResponse, status_code=status.HTTP_200_OK)
def download_certificate(
    id: int,
    service: CertificateService = Depends(get_certificate_service),
    current_user: User = Depends(get_current_user),
) -> FileResponse:
    try:
        certificate, file_path = service.get_certificate_file(id, current_user=current_user)
    except CertificateNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except CertificatePermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=f"{certificate.certificate_id}.pdf",
    )


@router.get("/verify/{certificate_id}", response_model=CertificateResponse)
def verify_certificate(
    certificate_id: str,
    service: CertificateService = Depends(get_certificate_service),
) -> CertificateResponse:
    try:
        return service.get_certificate_by_id(certificate_id)
    except CertificateNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
