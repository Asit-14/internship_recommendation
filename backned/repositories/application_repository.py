from sqlalchemy.orm import Session

from models.application_model import Application, ApplicationStatus
from models.internship_model import Internship
from models.user_model import User


class ApplicationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, application_id: int) -> Application | None:
        return self.db.query(Application).filter(Application.id == application_id).one_or_none()

    def get_by_user(self, user_id: int) -> list[Application]:
        return (
            self.db.query(Application)
            .filter(Application.user_id == user_id)
            .order_by(Application.applied_at.desc())
            .all()
        )

    def get_by_user_and_internship(self, user_id: int, internship_id: int) -> Application | None:
        return (
            self.db.query(Application)
            .filter(
                Application.user_id == user_id,
                Application.internship_id == internship_id,
            )
            .one_or_none()
        )

    def internship_exists(self, internship_id: int) -> bool:
        return (
            self.db.query(Internship.id)
            .filter(Internship.id == internship_id)
            .first()
            is not None
        )

    def create(self, *, user_id: int, internship_id: int, resume_url: str | None) -> Application:
        application = Application(
            user_id=user_id,
            internship_id=internship_id,
            status=ApplicationStatus.APPLIED,
            resume_url=resume_url,
        )
        self.db.add(application)
        self.db.commit()
        self.db.refresh(application)
        return application

    def update_status(self, application: Application, status: ApplicationStatus) -> Application:
        application.status = status
        self.db.add(application)
        self.db.commit()
        self.db.refresh(application)
        return application

    def get_internship_by_id(self, internship_id: int) -> Internship | None:
        return self.db.query(Internship).filter(Internship.id == internship_id).one_or_none()

    def get_internship_owner_id(self, internship_id: int) -> int | None:
        return (
            self.db.query(Internship.created_by)
            .filter(Internship.id == internship_id)
            .scalar()
        )

    def list_by_user_with_internship(self, user_id: int) -> list[tuple[Application, Internship]]:
        return (
            self.db.query(Application, Internship)
            .join(Internship, Application.internship_id == Internship.id)
            .filter(Application.user_id == user_id)
            .order_by(Application.applied_at.desc())
            .all()
        )

    def list_by_internship_with_user(
        self,
        internship_id: int,
    ) -> list[tuple[Application, User]]:
        return (
            self.db.query(Application, User)
            .join(User, Application.user_id == User.id)
            .filter(Application.internship_id == internship_id)
            .order_by(Application.applied_at.desc())
            .all()
        )

    def get_application_with_user_and_internship(
        self,
        application_id: int,
    ) -> tuple[Application, User, Internship] | None:
        result = (
            self.db.query(Application, User, Internship)
            .join(User, Application.user_id == User.id)
            .join(Internship, Application.internship_id == Internship.id)
            .filter(Application.id == application_id)
            .one_or_none()
        )
        if result is None:
            return None
        return result

    def get_application_with_internship(
        self,
        application_id: int,
    ) -> tuple[Application, Internship] | None:
        result = (
            self.db.query(Application, Internship)
            .join(Internship, Application.internship_id == Internship.id)
            .filter(Application.id == application_id)
            .one_or_none()
        )
        if result is None:
            return None
        return result