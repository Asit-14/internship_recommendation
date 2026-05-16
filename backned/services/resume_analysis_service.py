from ai.explanation import (
    build_resume_recommendation_explanation,
    identify_matched_skills,
    identify_skill_gaps,
)
from ai.resume_parser import parse_resume_file
from ai.resume_scoring import (
    build_required_experience_profile,
    build_resume_score_breakdown,
    calculate_experience_match_score,
)
from ai.scoring import (
    calculate_education_match_score,
    calculate_location_match_score,
    calculate_skill_match_score,
)
from ai.skill_extractor import normalize_skill_list
from models.user_model import User
from repositories.internship_repository import InternshipRepository
from schemas.resume_schema import ResumeRecommendationItem


class ResumeAnalysisServiceError(Exception):
    pass


class NoActiveInternshipsError(ResumeAnalysisServiceError):
    pass


class ResumeAnalysisService:
    def __init__(self, internship_repository: InternshipRepository):
        self.internship_repository = internship_repository

    def analyze_resume(
        self,
        *,
        filename: str,
        content_type: str | None,
        content: bytes,
        current_user: User | None = None,
    ) -> list[ResumeRecommendationItem]:
        parsed_resume = parse_resume_file(
            filename=filename,
            content_type=content_type,
            content=content,
        )

        profile_skills = current_user.skills if current_user and current_user.skills else []
        user_skills = normalize_skill_list([*profile_skills, *parsed_resume.skills])

        if not user_skills:
            raise ResumeAnalysisServiceError(
                "No skills could be identified. Please upload a more detailed resume."
            )

        user_location = parsed_resume.location or (current_user.location if current_user else None)
        user_education = parsed_resume.education_level or (current_user.education if current_user else None)
        if not user_education:
            user_education = ""

        internships = self.internship_repository.list()
        active_internships = [internship for internship in internships if internship.is_active]

        if not active_internships:
            raise NoActiveInternshipsError("No active internships are available for recommendations")

        recommendations: list[ResumeRecommendationItem] = []

        for internship in active_internships:
            skill_match = calculate_skill_match_score(user_skills, internship.skills_required)
            location_match = (
                calculate_location_match_score(user_location, internship.location)
                if user_location
                else 0.0
            )
            education_match, education_details = calculate_education_match_score(
                user_education,
                internship.title,
                internship.description,
            )

            required_experience = build_required_experience_profile(
                internship.title,
                internship.description,
            )
            experience_match_score, experience_details = calculate_experience_match_score(
                parsed_resume.experience,
                required_experience,
            )

            score_breakdown = build_resume_score_breakdown(
                skill_match=skill_match,
                location_match=location_match,
                education_match=education_match,
                experience_match=experience_match_score,
                experience_details=experience_details,
            )

            matched_skills = identify_matched_skills(user_skills, internship.skills_required)
            missing_skills = identify_skill_gaps(user_skills, internship.skills_required)

            explanation = build_resume_recommendation_explanation(
                matched_skills=matched_skills,
                missing_skills=missing_skills,
                score_breakdown=score_breakdown,
                user_location=user_location,
                internship_location=internship.location,
                user_education_level=education_details.user_level,
                required_education_level=education_details.required_level,
                user_experience=parsed_resume.experience,
                required_experience=required_experience,
            )

            recommendations.append(
                ResumeRecommendationItem(
                    internship_id=internship.id,
                    title=internship.title,
                    company_name=internship.company_name,
                    location=internship.location,
                    sector=internship.sector,
                    match_score=score_breakdown.total_score,
                    matched_skills=matched_skills,
                    missing_skills=missing_skills,
                    explanation=explanation,
                )
            )

        recommendations.sort(
            key=lambda item: item.match_score,
            reverse=True,
        )

        return recommendations[:5]
