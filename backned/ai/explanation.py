from ai.resume_parser import ExperienceProfile
from ai.resume_scoring import ResumeScoreBreakdown
from ai.scoring import ScoreBreakdown
from ai.skill_extractor import normalize_skill_list


def identify_matched_skills(user_skills: list[str], internship_skills: list[str]) -> list[str]:
    normalized_user_skills = set(normalize_skill_list(user_skills))
    normalized_internship_skills = normalize_skill_list(internship_skills)

    return [skill for skill in normalized_internship_skills if skill in normalized_user_skills]


def identify_skill_gaps(user_skills: list[str], internship_skills: list[str]) -> list[str]:
    normalized_user_skills = set(normalize_skill_list(user_skills))
    normalized_internship_skills = normalize_skill_list(internship_skills)

    return [skill for skill in normalized_internship_skills if skill not in normalized_user_skills]


def _format_education_level(level: str | None) -> str:
    if level is None:
        return "unspecified"

    return level.replace("_", " ")


def build_recommendation_explanation(
    *,
    matched_skills: list[str],
    missing_skills: list[str],
    score_breakdown: ScoreBreakdown,
    user_location: str,
    internship_location: str,
    user_education_level: str | None,
    required_education_level: str | None,
) -> str:
    explanation_parts: list[str] = []

    if matched_skills:
        top_matches = ", ".join(matched_skills[:3])
        explanation_parts.append(
            f"Strong skill alignment ({score_breakdown.skill_match:.2f}%) driven by {top_matches}."
        )
    else:
        explanation_parts.append(
            "No direct skill overlap detected, but the role may still fit based on other factors."
        )

    if score_breakdown.location_match >= 90:
        explanation_parts.append(
            f"Location is highly aligned with your preference ({user_location} vs {internship_location})."
        )
    elif score_breakdown.location_match > 0:
        explanation_parts.append(
            f"Location has partial overlap ({user_location} vs {internship_location})."
        )
    else:
        explanation_parts.append("Location alignment is low for this role.")

    if required_education_level is None:
        explanation_parts.append(
            "No explicit education requirement was detected in the internship description."
        )
    else:
        explanation_parts.append(
            "Education fit: "
            f"your profile ({_format_education_level(user_education_level)}) compared to "
            f"required level ({_format_education_level(required_education_level)})."
        )

    if missing_skills:
        top_gaps = ", ".join(missing_skills[:3])
        explanation_parts.append(f"Primary skill gaps to close: {top_gaps}.")
    else:
        explanation_parts.append("You currently cover all listed required skills for this internship.")

    explanation_parts.append(f"Overall weighted match score: {score_breakdown.total_score:.2f}%.")

    return " ".join(explanation_parts)


def _format_experience_profile(profile: ExperienceProfile) -> str:
    if profile.years is not None:
        years_text = f"{profile.years:.1f}".rstrip("0").rstrip(".")
        return f"{years_text} years"

    if profile.level is not None:
        return profile.level

    return "unspecified"


def build_resume_recommendation_explanation(
    *,
    matched_skills: list[str],
    missing_skills: list[str],
    score_breakdown: ResumeScoreBreakdown,
    user_location: str | None,
    internship_location: str,
    user_education_level: str | None,
    required_education_level: str | None,
    user_experience: ExperienceProfile,
    required_experience: ExperienceProfile,
) -> str:
    explanation_parts: list[str] = []

    if matched_skills:
        top_matches = ", ".join(matched_skills[:3])
        explanation_parts.append(
            f"Strong skill alignment ({score_breakdown.skill_match:.2f}%) driven by {top_matches}."
        )
    else:
        explanation_parts.append(
            "No direct skill overlap detected, but other factors may still align."
        )

    if user_location:
        if score_breakdown.location_match >= 90:
            explanation_parts.append(
                f"Location is highly aligned ({user_location} vs {internship_location})."
            )
        elif score_breakdown.location_match > 0:
            explanation_parts.append(
                f"Location has partial overlap ({user_location} vs {internship_location})."
            )
        else:
            explanation_parts.append("Location alignment is low for this role.")
    else:
        explanation_parts.append("Location was not found in the resume, so location fit is limited.")

    if required_education_level is None:
        explanation_parts.append(
            "No explicit education requirement was detected in the internship description."
        )
    else:
        explanation_parts.append(
            "Education fit: "
            f"your profile ({_format_education_level(user_education_level)}) compared to "
            f"required level ({_format_education_level(required_education_level)})."
        )

    if required_experience.years is None and required_experience.level is None:
        explanation_parts.append("No explicit experience requirement was detected for this role.")
    else:
        explanation_parts.append(
            "Experience fit: "
            f"your background ({_format_experience_profile(user_experience)}) compared to "
            f"required ({_format_experience_profile(required_experience)})."
        )

    if missing_skills:
        top_gaps = ", ".join(missing_skills[:3])
        explanation_parts.append(f"Primary skill gaps to close: {top_gaps}.")
    else:
        explanation_parts.append("You currently cover all listed required skills for this internship.")

    explanation_parts.append(
        f"Overall weighted match score: {score_breakdown.total_score:.2f}%."
    )

    return " ".join(explanation_parts)
