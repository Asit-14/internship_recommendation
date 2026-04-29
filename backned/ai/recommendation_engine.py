from dataclasses import dataclass
from typing import Sequence

from ai.explanation import (
    build_recommendation_explanation,
    identify_matched_skills,
    identify_skill_gaps,
)
from ai.scoring import ScoreBreakdown, ScoreWeights, calculate_weighted_score
from ai.skill_extractor import merge_user_skills
from models.internship_model import Internship
from schemas.recommendation_schema import RecommendationRequest


@dataclass(frozen=True)
class RecommendationResult:
    internship: Internship
    score_breakdown: ScoreBreakdown
    explanation: str
    matched_skills: list[str]
    skill_gap: list[str]


class RecommendationEngine:
    def __init__(self, *, weights: ScoreWeights | None = None):
        self.weights = weights or ScoreWeights()

    def recommend(
        self,
        *,
        user_profile: RecommendationRequest,
        internships: Sequence[Internship],
    ) -> tuple[list[RecommendationResult], list[str]]:
        normalized_user_skills = merge_user_skills(
            explicit_skills=user_profile.skills,
            resume_text=user_profile.resume_text,
        )

        preferences = user_profile.preferences.model_dump() if user_profile.preferences else None

        scored_recommendations: list[RecommendationResult] = []
        for internship in internships:
            score_breakdown, education_details = calculate_weighted_score(
                user_skills=normalized_user_skills,
                user_location=user_profile.location,
                user_education=user_profile.education,
                internship_skills=internship.skills_required,
                internship_location=internship.location,
                internship_title=internship.title,
                internship_description=internship.description,
                internship_sector=internship.sector,
                internship_company=internship.company_name,
                internship_stipend=internship.stipend,
                internship_duration=internship.duration,
                preferences=preferences,
                weights=self.weights,
            )

            matched_skills = identify_matched_skills(
                normalized_user_skills,
                internship.skills_required,
            )
            skill_gap = identify_skill_gaps(normalized_user_skills, internship.skills_required)

            explanation = build_recommendation_explanation(
                matched_skills=matched_skills,
                missing_skills=skill_gap,
                score_breakdown=score_breakdown,
                user_location=user_profile.location,
                internship_location=internship.location,
                user_education_level=education_details.user_level,
                required_education_level=education_details.required_level,
            )

            scored_recommendations.append(
                RecommendationResult(
                    internship=internship,
                    score_breakdown=score_breakdown,
                    explanation=explanation,
                    matched_skills=matched_skills,
                    skill_gap=skill_gap,
                )
            )

        scored_recommendations.sort(
            key=lambda recommendation: (
                recommendation.score_breakdown.total_score,
                recommendation.score_breakdown.skill_match,
            ),
            reverse=True,
        )

        return scored_recommendations[: user_profile.top_k], normalized_user_skills
