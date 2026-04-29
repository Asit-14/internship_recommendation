from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_current_user, require_roles
from models.user_model import User, UserRole
from repositories.certificate_repository import CertificateRepository
from schemas.certificate_schema import CertificateGenerateRequest, CertificateResponse
from services.certificate_service import (
    CertificateConflictError,
    CertificateNotFoundError,
    CertificatePermissionDeniedError,
    CertificateService,
    CertificateValidationError,
)


router = APIRouter(prefix="/certificate", tags=["Certificates"])


def get_certificate_service(db: Session = Depends(get_db)) -> CertificateService:
    return CertificateService(CertificateRepository(db))


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
