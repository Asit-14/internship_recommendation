from pydantic import BaseModel, Field


class ResumeRecommendationItem(BaseModel):
    internship_id: int
    title: str
    company_name: str
    location: str
    sector: str
    match_score: float = Field(ge=0, le=100)
    matched_skills: list[str]
    missing_skills: list[str]
    explanation: str
