from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_current_user
from models.user_model import User
from repositories.user_repository import UserRepository
from schemas.user_schema import ResumeUploadResponse, UserProfileResponse, UserProfileUpdateRequest
from services.user_service import EmptyProfileUpdateError, InvalidResumeFileError, UserService


router = APIRouter(prefix="/users", tags=["Users"])


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(UserRepository(db))


@router.get("/profile", response_model=UserProfileResponse, status_code=status.HTTP_200_OK)
def get_profile(
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> UserProfileResponse:
    user = service.get_profile(current_user)
    return UserProfileResponse.model_validate(user)


@router.put("/profile", response_model=UserProfileResponse, status_code=status.HTTP_200_OK)
def update_profile(
    payload: UserProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> UserProfileResponse:
    try:
        updated_user = service.update_profile(current_user, payload)
    except EmptyProfileUpdateError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return UserProfileResponse.model_validate(updated_user)


@router.post(
    "/upload-resume",
    response_model=ResumeUploadResponse,
    status_code=status.HTTP_200_OK,
)
async def upload_resume(
    resume: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> ResumeUploadResponse:
    try:
        return await service.upload_resume(current_user=current_user, file=resume)
    except InvalidResumeFileError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
