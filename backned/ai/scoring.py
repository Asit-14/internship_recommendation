from dataclasses import dataclass
from typing import Any

from ai.similarity import cosine_similarity, keyword_overlap_ratio, text_similarity
from ai.skill_extractor import normalize_skill_list


EDUCATION_LEVEL_RANK: dict[str, int] = {
    "high_school": 1,
    "diploma": 2,
    "bachelor": 3,
    "master": 4,
    "phd": 5,
}

EDUCATION_KEYWORDS: dict[str, tuple[str, ...]] = {
    "high_school": ("high school", "12th", "higher secondary"),
    "diploma": ("diploma", "associate degree"),
    "bachelor": (
        "bachelor",
        "b.tech",
        "b.e",
        "bs",
        "undergraduate",
        "graduation",
    ),
    "master": ("master", "m.tech", "ms", "postgraduate", "mba"),
    "phd": ("phd", "doctorate"),
}


@dataclass(frozen=True)
class ScoreWeights:
    skill_match: float = 0.5
    location_match: float = 0.2
    education_match: float = 0.2
    preference_match: float = 0.1

    def __post_init__(self) -> None:
        total = self.skill_match + self.location_match + self.education_match + self.preference_match
        if round(total, 6) != 1.0:
            raise ValueError("Score weights must add up to 1.0")


@dataclass(frozen=True)
class EducationMatchDetails:
    user_level: str | None
    required_level: str | None


@dataclass(frozen=True)
class ScoreBreakdown:
    skill_match: float
    location_match: float
    education_match: float
    preference_match: float
    total_score: float


def normalize_education_level(education_text: str | None) -> str | None:
    if not education_text:
        return None

    lowered = education_text.strip().lower()
    for level, keywords in EDUCATION_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            return level

    return None


def infer_required_education(*texts: str | None) -> str | None:
    lowered = " ".join(text.strip().lower() for text in texts if text)
    if not lowered:
        return None

    matched_levels: list[str] = []
    for level, keywords in EDUCATION_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            matched_levels.append(level)

    if not matched_levels:
        return None

    return max(matched_levels, key=lambda level: EDUCATION_LEVEL_RANK[level])


def calculate_skill_match_score(user_skills: list[str], internship_skills: list[str]) -> float:
    normalized_user_skills = normalize_skill_list(user_skills)
    normalized_internship_skills = normalize_skill_list(internship_skills)

    if not normalized_user_skills or not normalized_internship_skills:
        return 0.0

    cosine_score = cosine_similarity(normalized_user_skills, normalized_internship_skills)
    coverage_score = keyword_overlap_ratio(normalized_user_skills, normalized_internship_skills)

    return round(((cosine_score * 0.6) + (coverage_score * 0.4)) * 100, 2)


def calculate_location_match_score(user_location: str, internship_location: str) -> float:
    normalized_user_location = user_location.strip().lower()
    normalized_internship_location = internship_location.strip().lower()

    if not normalized_user_location or not normalized_internship_location:
        return 0.0

    if normalized_user_location == normalized_internship_location:
        return 100.0

    if (
        normalized_user_location in normalized_internship_location
        or normalized_internship_location in normalized_user_location
    ):
        return 90.0

    return round(text_similarity(normalized_user_location, normalized_internship_location) * 100, 2)


def calculate_education_match_score(
    user_education: str,
    internship_title: str,
    internship_description: str,
) -> tuple[float, EducationMatchDetails]:
    normalized_user_level = normalize_education_level(user_education)
    inferred_required_level = infer_required_education(internship_title, internship_description)

    details = EducationMatchDetails(
        user_level=normalized_user_level,
        required_level=inferred_required_level,
    )

    if inferred_required_level is None:
        return 100.0, details

    if normalized_user_level is None:
        return 0.0, details

    user_rank = EDUCATION_LEVEL_RANK[normalized_user_level]
    required_rank = EDUCATION_LEVEL_RANK[inferred_required_level]

    if user_rank >= required_rank:
        return 100.0, details

    rank_gap = required_rank - user_rank
    if rank_gap == 1:
        return 60.0, details

    if rank_gap == 2:
        return 30.0, details

    return 0.0, details


def _normalized_text_list(values: list[str] | None) -> list[str]:
    if not values:
        return []

    normalized: list[str] = []
    seen: set[str] = set()

    for value in values:
        cleaned = value.strip().lower()
        if not cleaned:
            continue

        if cleaned not in seen:
            seen.add(cleaned)
            normalized.append(cleaned)

    return normalized


def calculate_preference_match_score(
    preferences: dict[str, Any] | None,
    *,
    internship_sector: str,
    internship_company: str,
    internship_stipend: int,
    internship_duration: int,
    internship_location: str,
) -> float:
    if not preferences:
        return 100.0

    checks: list[float] = []

    preferred_sectors = _normalized_text_list(preferences.get("preferred_sectors"))
    if preferred_sectors:
        internship_sector_normalized = internship_sector.strip().lower()
        checks.append(100.0 if internship_sector_normalized in preferred_sectors else 0.0)

    preferred_companies = _normalized_text_list(preferences.get("preferred_companies"))
    if preferred_companies:
        internship_company_normalized = internship_company.strip().lower()
        company_match = any(
            preferred_company in internship_company_normalized
            or internship_company_normalized in preferred_company
            for preferred_company in preferred_companies
        )
        checks.append(100.0 if company_match else 0.0)

    minimum_stipend = preferences.get("minimum_stipend")
    if minimum_stipend is not None:
        checks.append(100.0 if internship_stipend >= minimum_stipend else 0.0)

    maximum_duration = preferences.get("maximum_duration_weeks")
    if maximum_duration is not None:
        checks.append(100.0 if internship_duration <= maximum_duration else 0.0)

    if preferences.get("remote_only"):
        location = internship_location.strip().lower()
        checks.append(100.0 if ("remote" in location or "hybrid" in location) else 0.0)

    if not checks:
        return 100.0

    return round(sum(checks) / len(checks), 2)


def calculate_weighted_score(
    *,
    user_skills: list[str],
    user_location: str,
    user_education: str,
    internship_skills: list[str],
    internship_location: str,
    internship_title: str,
    internship_description: str,
    internship_sector: str,
    internship_company: str,
    internship_stipend: int,
    internship_duration: int,
    preferences: dict[str, Any] | None,
    weights: ScoreWeights | None = None,
) -> tuple[ScoreBreakdown, EducationMatchDetails]:
    active_weights = weights or ScoreWeights()

    skill_match = calculate_skill_match_score(user_skills, internship_skills)
    location_match = calculate_location_match_score(user_location, internship_location)
    education_match, education_details = calculate_education_match_score(
        user_education,
        internship_title,
        internship_description,
    )
    preference_match = calculate_preference_match_score(
        preferences,
        internship_sector=internship_sector,
        internship_company=internship_company,
        internship_stipend=internship_stipend,
        internship_duration=internship_duration,
        internship_location=internship_location,
    )

    total_score = round(
        (skill_match * active_weights.skill_match)
        + (location_match * active_weights.location_match)
        + (education_match * active_weights.education_match)
        + (preference_match * active_weights.preference_match),
        2,
    )

    return (
        ScoreBreakdown(
            skill_match=skill_match,
            location_match=location_match,
            education_match=education_match,
            preference_match=preference_match,
            total_score=total_score,
        ),
        education_details,
    )
