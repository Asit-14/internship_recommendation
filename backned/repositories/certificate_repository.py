from sqlalchemy.orm import Session

from models.application_model import Application
from models.certificate_model import Certificate
from models.internship_model import Internship
from models.user_model import User


class CertificateRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_application_by_id(self, application_id: int) -> Application | None:
        return self.db.query(Application).filter(Application.id == application_id).one_or_none()

    def get_user_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).one_or_none()

    def get_internship_by_id(self, internship_id: int) -> Internship | None:
        return self.db.query(Internship).filter(Internship.id == internship_id).one_or_none()

    def get_by_id(self, certificate_db_id: int) -> Certificate | None:
        return self.db.query(Certificate).filter(Certificate.id == certificate_db_id).one_or_none()

    def get_by_user_and_internship(self, *, user_id: int, internship_id: int) -> Certificate | None:
        return (
            self.db.query(Certificate)
            .filter(Certificate.user_id == user_id, Certificate.internship_id == internship_id)
            .one_or_none()
        )

    def get_by_certificate_id(self, certificate_id: str) -> Certificate | None:
        return (
            self.db.query(Certificate)
            .filter(Certificate.certificate_id == certificate_id)
            .one_or_none()
        )

    def create(self, *, certificate_data: dict) -> Certificate:
        certificate = Certificate(**certificate_data)
        self.db.add(certificate)
        self.db.commit()
        self.db.refresh(certificate)
        return certificate
