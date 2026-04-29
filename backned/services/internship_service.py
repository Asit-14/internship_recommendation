from pydantic import ValidationError

from models.internship_model import Internship
from repositories.internship_repository import InternshipRepository
from schemas.internship_schema import (
    InternshipCreate,
    InternshipFilterParams,
    InternshipResponse,
    InternshipUpdate,
)


class InternshipNotFoundError(Exception):
    pass


class InvalidInternshipFilterError(Exception):
    pass


class InternshipAccessDeniedError(Exception):
    pass


class InternshipService:
    def __init__(self, internship_repository: InternshipRepository):
        self.internship_repository = internship_repository

    def create_internship(
        self,
        payload: InternshipCreate,
        *,
        created_by: int | None = None,
    ) -> InternshipResponse:
        internship_data = payload.model_dump()
        if created_by is not None:
            internship_data["created_by"] = created_by
        internship = self.internship_repository.create(internship_data=internship_data)
        return InternshipResponse.model_validate(internship)

    def get_internships(
        self,
        *,
        location: str | None = None,
        skills: list[str] | None = None,
        sector: str | None = None,
        stipend_min: int | None = None,
        stipend_max: int | None = None,
        duration_min: int | None = None,
        duration_max: int | None = None,
        user_skills: list[str] | None = None,
        only_active: bool | None = None,
    ) -> list[InternshipResponse]:
        try:
            filters = InternshipFilterParams(
                location=location,
                skills=skills,
                sector=sector,
                stipend_min=stipend_min,
                stipend_max=stipend_max,
                duration_min=duration_min,
                duration_max=duration_max,
            )
        except ValidationError as exc:
            raise InvalidInternshipFilterError(str(exc)) from exc

        internships = self.internship_repository.list(
            location=filters.location,
            sector=filters.sector,
            stipend_min=filters.stipend_min,
            stipend_max=filters.stipend_max,
            duration_min=filters.duration_min,
            duration_max=filters.duration_max,
            only_active=only_active,
        )

        if filters.skills:
            internships = [
                internship
                for internship in internships
                if self._matches_skill_filter(internship.skills_required, filters.skills)
            ]

        return [self._to_response(item, user_skills=user_skills) for item in internships]

    def get_company_internships(self, company_id: int) -> list[InternshipResponse]:
        internships = self.internship_repository.list_by_creator(company_id)
        return [InternshipResponse.model_validate(item) for item in internships]

    def get_internship_by_id(
        self,
        internship_id: int,
        *,
        user_skills: list[str] | None = None,
    ) -> InternshipResponse:
        internship = self.internship_repository.get_by_id(internship_id)
        if internship is None:
            raise InternshipNotFoundError("Internship not found")

        return self._to_response(internship, user_skills=user_skills)

    def update_internship(self, internship_id: int, payload: InternshipUpdate) -> InternshipResponse:
        internship = self.internship_repository.get_by_id(internship_id)
        if internship is None:
            raise InternshipNotFoundError("Internship not found")

        updates = payload.model_dump(exclude_unset=True, exclude_none=True)
        updated = self.internship_repository.update(internship, updates=updates)
        return InternshipResponse.model_validate(updated)

    def update_internship_for_company(
        self,
        internship_id: int,
        payload: InternshipUpdate,
        *,
        company_id: int,
    ) -> InternshipResponse:
        internship = self._get_owned_internship(internship_id, company_id)
        updates = payload.model_dump(exclude_unset=True, exclude_none=True)
        updated = self.internship_repository.update(internship, updates=updates)
        return InternshipResponse.model_validate(updated)

    def delete_internship(self, internship_id: int) -> None:
        internship = self.internship_repository.get_by_id(internship_id)
        if internship is None:
            raise InternshipNotFoundError("Internship not found")

        self.internship_repository.delete(internship)

    def delete_internship_for_company(self, internship_id: int, *, company_id: int) -> None:
        internship = self._get_owned_internship(internship_id, company_id)
        self.internship_repository.delete(internship)

    @staticmethod
    def calculate_skill_match_score(user_skills: list[str], internship_skills: list[str]) -> float:
        normalized_user_skills = {skill.strip().lower() for skill in user_skills if skill.strip()}
        normalized_internship_skills = {
            skill.strip().lower() for skill in internship_skills if skill.strip()
        }

        if not normalized_user_skills or not normalized_internship_skills:
            return 0.0

        matched = normalized_user_skills.intersection(normalized_internship_skills)
        return round((len(matched) / len(normalized_internship_skills)) * 100, 2)

    def _to_response(
        self,
        internship: Internship,
        *,
        user_skills: list[str] | None = None,
    ) -> InternshipResponse:
        response = InternshipResponse.model_validate(internship)

        if user_skills:
            score = self.calculate_skill_match_score(user_skills, internship.skills_required)
            return response.model_copy(update={"skill_match_score": score})

        return response

    @staticmethod
    def _matches_skill_filter(internship_skills: list[str], requested_skills: list[str]) -> bool:
        internship_skill_set = {skill.strip().lower() for skill in internship_skills if skill.strip()}
        requested_skill_set = {skill.strip().lower() for skill in requested_skills if skill.strip()}

        if not internship_skill_set or not requested_skill_set:
            return False

        return not internship_skill_set.isdisjoint(requested_skill_set)

    def _get_owned_internship(self, internship_id: int, company_id: int) -> Internship:
        internship = self.internship_repository.get_by_id(internship_id)
        if internship is None:
            raise InternshipNotFoundError("Internship not found")

        if internship.created_by != company_id:
            raise InternshipAccessDeniedError("You do not have access to this internship")

        return internship