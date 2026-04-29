from pydantic import BaseModel

from schemas.auth_schema import UserResponse
from schemas.internship_schema import InternshipResponse


class AdminCompanyDetailResponse(BaseModel):
    company: UserResponse
    internships: list[InternshipResponse]
