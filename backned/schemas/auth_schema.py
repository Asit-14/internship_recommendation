import re
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class RoleEnum(str, Enum):
    student = "student"
    company = "company"
    admin = "admin"


def _normalize_name(value: str) -> str:
    normalized = " ".join(value.split())
    if len(normalized) < 2:
        raise ValueError("Name must be at least 2 characters long")
    return normalized


def _validate_password_strength(value: str) -> str:
    pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z\d]).{8,128}$"
    if not re.match(pattern, value):
        raise ValueError(
            "Password must include uppercase, lowercase, number, and special character"
        )
    return value


class SignupRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return _normalize_name(value)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        return _validate_password_strength(value)


class CompanySignupRequest(BaseModel):
    company_name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("company_name")
    @classmethod
    def validate_company_name(cls, value: str) -> str:
        return _normalize_name(value)

    @field_validator("password")
    @classmethod
    def validate_company_password_strength(cls, value: str) -> str:
        return _validate_password_strength(value)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: RoleEnum
    is_verified: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
