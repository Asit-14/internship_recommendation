from sqlalchemy.orm import Session

from models.application_model import Application
from models.internship_model import Internship
from models.internship_progress_model import InternshipProgress


class ProgressRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_application_by_id(self, application_id: int) -> Application | None:
        return self.db.query(Application).filter(Application.id == application_id).one_or_none()

    def get_internship_by_id(self, internship_id: int) -> Internship | None:
        return self.db.query(Internship).filter(Internship.id == internship_id).one_or_none()

    def get_by_application_and_week(
        self,
        *,
        application_id: int,
        week_number: int,
    ) -> InternshipProgress | None:
        return (
            self.db.query(InternshipProgress)
            .filter(
                InternshipProgress.application_id == application_id,
                InternshipProgress.week_number == week_number,
            )
            .one_or_none()
        )

    def create(self, *, progress_data: dict) -> InternshipProgress:
        progress = InternshipProgress(**progress_data)
        self.db.add(progress)
        self.db.commit()
        self.db.refresh(progress)
        return progress

    def update(self, progress: InternshipProgress, *, updates: dict) -> InternshipProgress:
        for field, value in updates.items():
            setattr(progress, field, value)

        self.db.commit()
        self.db.refresh(progress)
        return progress

    def list_by_application(self, *, application_id: int) -> list[InternshipProgress]:
        return (
            self.db.query(InternshipProgress)
            .filter(InternshipProgress.application_id == application_id)
            .order_by(InternshipProgress.week_number.asc(), InternshipProgress.created_at.asc())
            .all()
        )
