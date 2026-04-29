from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_current_user_optional
from models.user_model import User
from repositories.internship_repository import InternshipRepository
from schemas.recommendation_schema import RecommendationRequest, RecommendationResponse
from services.recommendation_service import (
    NoActiveInternshipsError,
    RecommendationService,
    RecommendationServiceError,
)


router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


def get_recommendation_service(db: Session = Depends(get_db)) -> RecommendationService:
    return RecommendationService(InternshipRepository(db))


@router.post("/", response_model=RecommendationResponse, status_code=status.HTTP_200_OK)
def recommend_internships(
    payload: RecommendationRequest,
    service: RecommendationService = Depends(get_recommendation_service),
    current_user: User | None = Depends(get_current_user_optional),
) -> RecommendationResponse:
    try:
        return service.get_recommendations(payload, current_user=current_user)
    except NoActiveInternshipsError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except RecommendationServiceError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
