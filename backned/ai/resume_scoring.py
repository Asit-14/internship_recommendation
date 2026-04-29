from dataclasses import dataclass

from ai.resume_parser import ExperienceProfile, extract_experience_profile


EXPERIENCE_LEVEL_RANK = {
    "entry": 1,
    "junior": 2,
    "mid": 3,
    "senior": 4,
}


@dataclass(frozen=True)
class ResumeScoreBreakdown:
    skill_match: float
    location_match: float
    education_match: float
    experience_match: float
    total_score: float


def calculate_experience_match_score(
    user_profile: ExperienceProfile,
    required_profile: ExperienceProfile,
) -> float:
    if required_profile.years is None and required_profile.level is None:
        return 100.0

    if user_profile.years is None and user_profile.level is None:
        return 0.0

    if required_profile.years is not None:
        if user_profile.years is None:
            return 0.0

        if user_profile.years >= required_profile.years:
            return 100.0

        gap = required_profile.years - user_profile.years
        if gap <= 1:
            return 60.0
        if gap <= 2:
            return 30.0
        return 0.0

    if required_profile.level is None or user_profile.level is None:
        return 0.0

    user_rank = EXPERIENCE_LEVEL_RANK.get(user_profile.level, 0)
    required_rank = EXPERIENCE_LEVEL_RANK.get(required_profile.level, 0)

    if user_rank >= required_rank:
        return 100.0

    gap = required_rank - user_rank
    if gap == 1:
        return 60.0
    if gap == 2:
        return 30.0

    return 0.0


def extract_required_experience(*texts: str | None) -> ExperienceProfile:
    combined = " ".join(text.strip() for text in texts if text)
    return extract_experience_profile(combined)


def build_resume_score_breakdown(
    *,
    skill_match: float,
    location_match: float,
    education_match: float,
    experience_match: float,
) -> ResumeScoreBreakdown:
    total_score = round(
        (skill_match * 0.5)
        + (education_match * 0.2)
        + (location_match * 0.2)
        + (experience_match * 0.1),
        2,
    )

    return ResumeScoreBreakdown(
        skill_match=skill_match,
        location_match=location_match,
        education_match=education_match,
        experience_match=experience_match,
        total_score=total_score,
    )
