from __future__ import annotations

from sqlalchemy.orm import Session

from models.internship_model import Internship


class InternshipRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, *, internship_data: dict) -> Internship:
        internship = Internship(**internship_data)
        self.db.add(internship)
        self.db.commit()
        self.db.refresh(internship)
        return internship

    def get_by_id(self, internship_id: int) -> Internship | None:
        return self.db.query(Internship).filter(Internship.id == internship_id).one_or_none()

    def list(
        self,
        *,
        location: str | None = None,
        sector: str | None = None,
        stipend_min: int | None = None,
        stipend_max: int | None = None,
        duration_min: int | None = None,
        duration_max: int | None = None,
        created_by: int | None = None,
        only_active: bool | None = None,
    ) -> list[Internship]:
        query = self.db.query(Internship)

        if location:
            query = query.filter(Internship.location.ilike(f"%{location}%"))

        if sector:
            query = query.filter(Internship.sector.ilike(f"%{sector}%"))

        if stipend_min is not None:
            query = query.filter(Internship.stipend >= stipend_min)

        if stipend_max is not None:
            query = query.filter(Internship.stipend <= stipend_max)

        if duration_min is not None:
            query = query.filter(Internship.duration >= duration_min)

        if duration_max is not None:
            query = query.filter(Internship.duration <= duration_max)

        if created_by is not None:
            query = query.filter(Internship.created_by == created_by)

        if only_active is True:
            query = query.filter(Internship.is_active.is_(True))

        if only_active is False:
            query = query.filter(Internship.is_active.is_(False))

        return query.order_by(Internship.created_at.desc()).all()

    def list_by_creator(self, creator_id: int) -> list[Internship]:
        return self.list(created_by=creator_id)

    def update(self, internship: Internship, *, updates: dict) -> Internship:
        for field, value in updates.items():
            setattr(internship, field, value)

        self.db.commit()
        self.db.refresh(internship)
        return internship

    def delete(self, internship: Internship) -> None:
        self.db.delete(internship)
        self.db.commit()