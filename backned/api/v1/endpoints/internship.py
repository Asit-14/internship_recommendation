from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import require_roles
from models.user_model import User, UserRole
from repositories.internship_repository import InternshipRepository
from schemas.internship_schema import (
    CompanyInternshipCreate,
    InternshipCreate,
    InternshipResponse,
    InternshipUpdate,
)
from services.internship_service import (
    InternshipAccessDeniedError,
    InternshipNotFoundError,
    InternshipService,
    InvalidInternshipFilterError,
)


router = APIRouter(prefix="/internships", tags=["Internships"])
DEFAULT_COMPANY_SECTOR = "General"


def get_internship_service(db: Session = Depends(get_db)) -> InternshipService:
    return InternshipService(InternshipRepository(db))


def _normalize_query_skills(raw_values: list[str] | None) -> list[str] | None:
    if not raw_values:
        return None

    normalized: list[str] = []
    seen: set[str] = set()

    for raw in raw_values:
        for value in raw.split(","):
            skill = value.strip()
            if not skill:
                continue

            lowered = skill.lower()
            if lowered not in seen:
                seen.add(lowered)
                normalized.append(skill)

    return normalized or None


@router.post("/", response_model=InternshipResponse, status_code=status.HTTP_201_CREATED)
def create_internship(
    payload: CompanyInternshipCreate,
    service: InternshipService = Depends(get_internship_service),
    current_user: User = Depends(require_roles(UserRole.company)),
) -> InternshipResponse:
    full_payload = InternshipCreate(
        **payload.model_dump(),
        company_name=current_user.name,
        sector=DEFAULT_COMPANY_SECTOR,
    )
    return service.create_internship(full_payload, created_by=current_user.id)


@router.get("/", response_model=list[InternshipResponse], status_code=status.HTTP_200_OK)
def get_internships(
    location: str | None = Query(default=None, max_length=255),
    skills: list[str] | None = Query(default=None),
    sector: str | None = Query(default=None, max_length=100),
    stipend_min: int | None = Query(default=None, ge=0),
    stipend_max: int | None = Query(default=None, ge=0),
    duration_min: int | None = Query(default=None, ge=1),
    duration_max: int | None = Query(default=None, ge=1),
    user_skills: list[str] | None = Query(
        default=None,
        description="Optional skills used to compute skill_match_score",
    ),
    service: InternshipService = Depends(get_internship_service),
) -> list[InternshipResponse]:
    normalized_skills = _normalize_query_skills(skills)
    normalized_user_skills = _normalize_query_skills(user_skills)

    try:
        return service.get_internships(
            location=location,
            skills=normalized_skills,
            sector=sector,
            stipend_min=stipend_min,
            stipend_max=stipend_max,
            duration_min=duration_min,
            duration_max=duration_max,
            user_skills=normalized_user_skills,
            only_active=True,
        )
    except InvalidInternshipFilterError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/{internship_id}", response_model=InternshipResponse, status_code=status.HTTP_200_OK)
def get_internship_by_id(
    internship_id: int,
    user_skills: list[str] | None = Query(
        default=None,
        description="Optional skills used to compute skill_match_score",
    ),
    service: InternshipService = Depends(get_internship_service),
) -> InternshipResponse:
    normalized_user_skills = _normalize_query_skills(user_skills)

    try:
        return service.get_internship_by_id(internship_id, user_skills=normalized_user_skills)
    except InternshipNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/{internship_id}", response_model=InternshipResponse, status_code=status.HTTP_200_OK)
def update_internship(
    internship_id: int,
    payload: InternshipUpdate,
    service: InternshipService = Depends(get_internship_service),
    _: User = Depends(require_roles(UserRole.admin)),
) -> InternshipResponse:
    try:
        return service.update_internship(internship_id, payload)
    except InternshipNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.put("/{internship_id}", response_model=InternshipResponse, status_code=status.HTTP_200_OK)
def replace_internship(
    internship_id: int,
    payload: InternshipUpdate,
    service: InternshipService = Depends(get_internship_service),
    current_user: User = Depends(require_roles(UserRole.company, UserRole.admin)),
) -> InternshipResponse:
    try:
        if current_user.role == UserRole.admin:
            return service.update_internship(internship_id, payload)

        return service.update_internship_for_company(
            internship_id,
            payload,
            company_id=current_user.id,
        )
    except InternshipNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except InternshipAccessDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@router.delete("/{internship_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_internship(
    internship_id: int,
    service: InternshipService = Depends(get_internship_service),
    current_user: User = Depends(require_roles(UserRole.company)),
) -> Response:
    try:
        service.delete_internship_for_company(internship_id, company_id=current_user.id)
    except InternshipNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except InternshipAccessDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)