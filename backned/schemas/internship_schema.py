from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from schemas.validators import normalize_optional_text as _normalize_optional_text
from schemas.validators import normalize_skills as _normalize_skills


def _normalize_required_text(value: str) -> str:
    normalized = _normalize_optional_text(value)
    if normalized is None:
        raise ValueError("Field is required")
    return normalized


def _normalize_required_skills(value: list[str]) -> list[str]:
    normalized = _normalize_skills(value)
    if normalized is None:
        raise ValueError("Skills are required")
    return normalized


class InternshipCreate(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    description: str = Field(min_length=10)
    company_name: str = Field(min_length=2, max_length=255)
    location: str = Field(min_length=2, max_length=255)
    skills_required: list[str] = Field(min_length=1)
    sector: str = Field(min_length=2, max_length=100)
    duration: int = Field(ge=1, description="Internship duration in weeks")
    stipend: int = Field(ge=0)
    is_active: bool = True

    @field_validator("title", "description", "company_name", "location", "sector")
    @classmethod
    def validate_text_fields(cls, value: str) -> str:
        return _normalize_required_text(value)

    @field_validator("skills_required")
    @classmethod
    def validate_skills(cls, value: list[str]) -> list[str]:
        return _normalize_required_skills(value)


class CompanyInternshipCreate(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    description: str = Field(min_length=10)
    location: str = Field(min_length=2, max_length=255)
    skills_required: list[str] = Field(min_length=1)
    duration: int = Field(ge=1, description="Internship duration in weeks")
    stipend: int = Field(ge=0)
    is_active: bool = True

    @field_validator("title", "description", "location")
    @classmethod
    def validate_text_fields(cls, value: str) -> str:
        return _normalize_required_text(value)

    @field_validator("skills_required")
    @classmethod
    def validate_skills(cls, value: list[str]) -> list[str]:
        return _normalize_required_skills(value)


class InternshipUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = Field(default=None, min_length=10)
    company_name: str | None = Field(default=None, min_length=2, max_length=255)
    location: str | None = Field(default=None, min_length=2, max_length=255)
    skills_required: list[str] | None = Field(default=None, min_length=1)
    sector: str | None = Field(default=None, min_length=2, max_length=100)
    duration: int | None = Field(default=None, ge=1)
    stipend: int | None = Field(default=None, ge=0)
    is_active: bool | None = None

    @field_validator("title", "description", "company_name", "location", "sector")
    @classmethod
    def validate_optional_text_fields(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)

    @field_validator("skills_required")
    @classmethod
    def validate_optional_skills(cls, value: list[str] | None) -> list[str] | None:
        return _normalize_skills(value)

    @model_validator(mode="after")
    def validate_has_update_payload(self) -> "InternshipUpdate":
        if not self.model_dump(exclude_unset=True):
            raise ValueError("At least one field must be provided for update")
        return self


class InternshipFilterParams(BaseModel):
    location: str | None = None
    skills: list[str] | None = None
    sector: str | None = None
    stipend_min: int | None = Field(default=None, ge=0)
    stipend_max: int | None = Field(default=None, ge=0)
    duration_min: int | None = Field(default=None, ge=1)
    duration_max: int | None = Field(default=None, ge=1)

    @field_validator("location", "sector")
    @classmethod
    def validate_optional_filter_text(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)

    @field_validator("skills")
    @classmethod
    def validate_filter_skills(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None
        return _normalize_skills(value)

    @model_validator(mode="after")
    def validate_numeric_ranges(self) -> "InternshipFilterParams":
        if self.stipend_min is not None and self.stipend_max is not None:
            if self.stipend_min > self.stipend_max:
                raise ValueError("stipend_min cannot be greater than stipend_max")

        if self.duration_min is not None and self.duration_max is not None:
            if self.duration_min > self.duration_max:
                raise ValueError("duration_min cannot be greater than duration_max")

        return self


class InternshipResponse(BaseModel):
    id: int
    title: str
    description: str
    company_name: str
    location: str
    skills_required: list[str]
    sector: str
    created_by: int | None = None
    duration: int
    stipend: int
    is_active: bool
    created_at: datetime
    skill_match_score: float | None = Field(default=None, ge=0, le=100)

    model_config = ConfigDict(from_attributes=True)