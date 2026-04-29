from pydantic import BaseModel, Field, field_validator

from schemas.validators import normalize_optional_text as _normalize_optional_text
from schemas.validators import normalize_skills as _normalize_skills


def _normalize_optional_text_list(values: list[str] | None) -> list[str] | None:
    if values is None:
        return None

    normalized_values: list[str] = []
    seen: set[str] = set()

    for value in values:
        normalized = value.strip()
        if not normalized:
            continue

        lowered = normalized.lower()
        if lowered not in seen:
            seen.add(lowered)
            normalized_values.append(normalized)

    if not normalized_values:
        raise ValueError("List must contain at least one non-empty value")

    return normalized_values


class RecommendationPreferences(BaseModel):
    preferred_sectors: list[str] | None = None
    preferred_companies: list[str] | None = None
    minimum_stipend: int | None = Field(default=None, ge=0)
    maximum_duration_weeks: int | None = Field(default=None, ge=1)
    remote_only: bool = False

    @field_validator("preferred_sectors", "preferred_companies")
    @classmethod
    def validate_optional_text_list(cls, value: list[str] | None) -> list[str] | None:
        return _normalize_optional_text_list(value)


class RecommendationRequest(BaseModel):
    skills: list[str] | None = None
    resume_text: str | None = Field(default=None, min_length=20)
    education: str | None = Field(default=None, min_length=2, max_length=100)
    location: str | None = Field(default=None, min_length=2, max_length=255)
    preferences: RecommendationPreferences | None = None
    top_k: int = Field(default=5, ge=3, le=5)

    @field_validator("skills")
    @classmethod
    def validate_skills(cls, value: list[str] | None) -> list[str] | None:
        return _normalize_skills(value)

    @field_validator("resume_text", "education", "location")
    @classmethod
    def validate_text_fields(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)


class ScoreBreakdownResponse(BaseModel):
    skill_match: float = Field(ge=0, le=100)
    location_match: float = Field(ge=0, le=100)
    education_match: float = Field(ge=0, le=100)
    preference_match: float = Field(ge=0, le=100)
    total_score: float = Field(ge=0, le=100)


class RecommendationItemResponse(BaseModel):
    internship_id: int
    title: str
    company_name: str
    location: str
    sector: str
    match_score: float = Field(ge=0, le=100)
    score_breakdown: ScoreBreakdownResponse
    explanation: str
    matched_skills: list[str]
    skill_gap: list[str]


class RecommendationResponse(BaseModel):
    normalized_user_skills: list[str]
    evaluated_internships_count: int = Field(ge=0)
    recommendations: list[RecommendationItemResponse]
