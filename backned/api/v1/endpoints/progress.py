from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_current_user
from models.user_model import User
from repositories.progress_repository import ProgressRepository
from schemas.progress_schema import ProgressCreate, ProgressResponse
from services.progress_service import (
    ProgressConflictError,
    ProgressNotFoundError,
    ProgressPermissionDeniedError,
    ProgressService,
    ProgressValidationError,
)


router = APIRouter(prefix="/progress", tags=["Internship Progress"])


def get_progress_service(db: Session = Depends(get_db)) -> ProgressService:
    return ProgressService(ProgressRepository(db))


@router.post("/", response_model=ProgressResponse, status_code=status.HTTP_201_CREATED)
def add_progress(
    payload: ProgressCreate,
    service: ProgressService = Depends(get_progress_service),
    current_user: User = Depends(get_current_user),
) -> ProgressResponse:
    try:
        return service.add_progress(payload, current_user=current_user)
    except ProgressNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ProgressPermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ProgressConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except ProgressValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/{application_id}", response_model=list[ProgressResponse], status_code=status.HTTP_200_OK)
def get_progress_logs(
    application_id: int,
    service: ProgressService = Depends(get_progress_service),
    current_user: User = Depends(get_current_user),
) -> list[ProgressResponse]:
    try:
        return service.get_progress_logs(application_id, current_user=current_user)
    except ProgressNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ProgressPermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
