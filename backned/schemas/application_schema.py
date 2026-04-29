from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ApplicationStatusEnum(str, Enum):
    APPLIED = "APPLIED"
    UNDER_REVIEW = "UNDER_REVIEW"
    SHORTLISTED = "SHORTLISTED"
    SELECTED = "SELECTED"
    IN_PROGRESS = "IN_PROGRESS"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"


class ApplicationCreateRequest(BaseModel):
    internship_id: int = Field(gt=0)


class ApplicationStatusUpdateRequest(BaseModel):
    status: ApplicationStatusEnum


class ApplicationResponse(BaseModel):
    id: int
    user_id: int
    internship_id: int
    status: ApplicationStatusEnum
    resume_url: str | None = None
    applied_at: datetime
    updated_at: datetime
    internship_title: str | None = None
    company_name: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ApplicantProfileResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str | None = None
    location: str | None = None
    education: str | None = None
    college_name: str | None = None
    branch: str | None = None
    graduation_year: int | None = None
    skills: list[str] = Field(default_factory=list)
    resume_url: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ApplicantSummaryResponse(BaseModel):
    application_id: int
    internship_id: int
    status: ApplicationStatusEnum
    applied_at: datetime
    resume_url: str | None = None
    student: ApplicantProfileResponse


class ApplicationDetailResponse(BaseModel):
    id: int
    internship_id: int
    status: ApplicationStatusEnum
    applied_at: datetime
    updated_at: datetime
    resume_url: str | None = None
    internship_title: str | None = None
    company_name: str | None = None
    student: ApplicantProfileResponse