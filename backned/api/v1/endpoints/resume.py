from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from ai.resume_parser import ResumeParsingError
from core.database import get_db
from core.security import get_current_user_optional
from models.user_model import User
from repositories.internship_repository import InternshipRepository
from schemas.resume_schema import ResumeRecommendationItem
from services.resume_analysis_service import (
    NoActiveInternshipsError,
    ResumeAnalysisService,
    ResumeAnalysisServiceError,
)


router = APIRouter(prefix="/resume", tags=["Resume"])

MAX_RESUME_BYTES = 5 * 1024 * 1024


def get_resume_analysis_service(db: Session = Depends(get_db)) -> ResumeAnalysisService:
    return ResumeAnalysisService(InternshipRepository(db))


@router.post("/analyze", response_model=list[ResumeRecommendationItem], status_code=status.HTTP_200_OK)
async def analyze_resume(
    resume: UploadFile = File(...),
    service: ResumeAnalysisService = Depends(get_resume_analysis_service),
    current_user: User | None = Depends(get_current_user_optional),
) -> list[ResumeRecommendationItem]:
    try:
        content = await resume.read()
        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded resume is empty.",
            )
        if len(content) > MAX_RESUME_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resume file exceeds the 5 MB limit.",
            )

        return service.analyze_resume(
            filename=resume.filename or "resume",
            content_type=resume.content_type,
            content=content,
            current_user=current_user,
        )
    except ResumeParsingError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except NoActiveInternshipsError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ResumeAnalysisServiceError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
