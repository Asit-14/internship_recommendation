import re
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from models.user_model import UserRole
from schemas.validators import normalize_optional_text as _normalize_optional_text


_PHONE_PATTERN = re.compile(r"^\+?[0-9]{7,15}$")
_MAX_GRADUATION_YEAR = datetime.now(timezone.utc).year + 10


def _normalize_skills_for_profile(value: list[str] | None) -> list[str] | None:
    if value is None:
        return None

    normalized_skills: list[str] = []
    seen: set[str] = set()

    for skill in value:
        cleaned = " ".join(skill.split()).strip()
        if not cleaned:
            continue

        lowered = cleaned.lower()
        if lowered not in seen:
            seen.add(lowered)
            normalized_skills.append(cleaned)

    return normalized_skills


class UserProfileResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole
    is_verified: bool

    phone: str | None = None
    location: str | None = None
    education: str | None = None
    college_name: str | None = None
    branch: str | None = None
    graduation_year: int | None = None
    skills: list[str] = Field(default_factory=list)
    resume_url: str | None = None
    
    # Company specific fields
    company_description: str | None = None
    website: str | None = None
    industry: str | None = None
    company_size: str | None = None
    established_year: int | None = None

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserProfileUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    phone: str | None = Field(default=None, max_length=20)
    location: str | None = Field(default=None, max_length=255)
    education: str | None = Field(default=None, max_length=120)
    college_name: str | None = Field(default=None, max_length=255)
    branch: str | None = Field(default=None, max_length=120)
    graduation_year: int | None = Field(default=None, ge=1950, le=_MAX_GRADUATION_YEAR)
    skills: list[str] | None = None
    
    # Company specific fields
    company_description: str | None = Field(default=None, max_length=1000)
    website: str | None = Field(default=None, max_length=255)
    industry: str | None = Field(default=None, max_length=120)
    company_size: str | None = Field(default=None, max_length=50)
    established_year: int | None = Field(default=None, ge=1800, le=_MAX_GRADUATION_YEAR)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return None

        normalized = " ".join(value.split())
        if len(normalized) < 2:
            raise ValueError("Name must be at least 2 characters long")
        return normalized

    @field_validator(
        "location", "education", "college_name", "branch",
        "company_description", "website", "industry", "company_size"
    )
    @classmethod
    def validate_optional_text_fields(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        if value is None:
            return None

        normalized = value.strip()
        if not _PHONE_PATTERN.match(normalized):
            raise ValueError("Phone must contain 7 to 15 digits and optional leading +")
        return normalized

    @field_validator("skills")
    @classmethod
    def validate_skills(cls, value: list[str] | None) -> list[str] | None:
        return _normalize_skills_for_profile(value)

    @model_validator(mode="after")
    def validate_has_payload(self) -> "UserProfileUpdateRequest":
        if not self.model_dump(exclude_unset=True):
            raise ValueError("At least one profile field must be provided for update")
        return self


class ResumeUploadResponse(BaseModel):
    resume_url: str


class DeleteAccountRequest(BaseModel):
    password: str
    confirmation: str = Field(..., description="Must be 'DELETE'")

    @field_validator("confirmation")
    @classmethod
    def validate_confirmation(cls, value: str) -> str:
        if value != "DELETE":
            raise ValueError("Please type 'DELETE' to confirm account deletion")
        return value
