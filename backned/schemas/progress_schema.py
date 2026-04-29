from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from schemas.validators import normalize_optional_text as _normalize_optional_text


class ProgressCreate(BaseModel):
    application_id: int = Field(gt=0)
    week_number: int = Field(gt=0)
    work_done: str | None = Field(default=None, min_length=5)
    mentor_feedback: str | None = Field(default=None, min_length=2)

    @field_validator("work_done", "mentor_feedback")
    @classmethod
    def validate_text_fields(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value)

    @model_validator(mode="after")
    def validate_payload_has_content(self) -> "ProgressCreate":
        if self.work_done is None and self.mentor_feedback is None:
            raise ValueError("Either work_done or mentor_feedback must be provided")
        return self


class ProgressResponse(BaseModel):
    id: int
    application_id: int
    week_number: int
    work_done: str
    mentor_feedback: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
