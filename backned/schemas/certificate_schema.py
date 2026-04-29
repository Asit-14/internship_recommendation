from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CertificateGenerateRequest(BaseModel):
    application_id: int = Field(gt=0)


class CertificateResponse(BaseModel):
    id: int
    user_id: int
    internship_id: int
    certificate_id: str
    certificate_url: str
    issued_at: datetime

    model_config = ConfigDict(from_attributes=True)
