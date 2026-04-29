from ai.recommendation_engine import RecommendationEngine
from models.user_model import User
from repositories.internship_repository import InternshipRepository
from schemas.recommendation_schema import (
    RecommendationItemResponse,
    RecommendationRequest,
    RecommendationResponse,
    ScoreBreakdownResponse,
)


class RecommendationServiceError(Exception):
    pass


class NoActiveInternshipsError(RecommendationServiceError):
    pass


class RecommendationService:
    def __init__(
        self,
        internship_repository: InternshipRepository,
        recommendation_engine: RecommendationEngine | None = None,
    ):
        self.internship_repository = internship_repository
        self.recommendation_engine = recommendation_engine or RecommendationEngine()

    def get_recommendations(
        self,
        payload: RecommendationRequest,
        *,
        current_user: User | None = None,
    ) -> RecommendationResponse:
        resolved_payload = self._resolve_payload(payload, current_user=current_user)

        internships = self.internship_repository.list()
        active_internships = [internship for internship in internships if internship.is_active]

        if not active_internships:
            raise NoActiveInternshipsError("No active internships are available for recommendations")

        recommendations, normalized_user_skills = self.recommendation_engine.recommend(
            user_profile=resolved_payload,
            internships=active_internships,
        )

        response_items = [
            RecommendationItemResponse(
                internship_id=result.internship.id,
                title=result.internship.title,
                company_name=result.internship.company_name,
                location=result.internship.location,
                sector=result.internship.sector,
                match_score=result.score_breakdown.total_score,
                score_breakdown=ScoreBreakdownResponse(
                    skill_match=result.score_breakdown.skill_match,
                    location_match=result.score_breakdown.location_match,
                    education_match=result.score_breakdown.education_match,
                    preference_match=result.score_breakdown.preference_match,
                    total_score=result.score_breakdown.total_score,
                ),
                explanation=result.explanation,
                matched_skills=result.matched_skills,
                skill_gap=result.skill_gap,
            )
            for result in recommendations
        ]

        return RecommendationResponse(
            normalized_user_skills=normalized_user_skills,
            evaluated_internships_count=len(active_internships),
            recommendations=response_items,
        )

    def _resolve_payload(
        self,
        payload: RecommendationRequest,
        *,
        current_user: User | None,
    ) -> RecommendationRequest:
        profile_skills = current_user.skills if current_user else None
        profile_education = current_user.education if current_user else None
        profile_location = current_user.location if current_user else None

        resolved_skills = payload.skills if payload.skills is not None else profile_skills
        resolved_education = payload.education or profile_education
        resolved_location = payload.location or profile_location

        if not resolved_education:
            raise RecommendationServiceError(
                "Education is required. Update profile or pass education in the request."
            )

        if not resolved_location:
            raise RecommendationServiceError(
                "Location is required. Update profile or pass location in the request."
            )

        if not resolved_skills and not payload.resume_text:
            raise RecommendationServiceError(
                "Provide skills/resume_text in request, or save skills in your profile."
            )

        return RecommendationRequest(
            skills=resolved_skills or None,
            resume_text=payload.resume_text,
            education=resolved_education,
            location=resolved_location,
            preferences=payload.preferences,
            top_k=payload.top_k,
        )
