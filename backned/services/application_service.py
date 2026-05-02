from pathlib import Path

from sqlalchemy.exc import IntegrityError

from models.application_model import Application, ApplicationStatus
from models.internship_model import Internship
from models.user_model import User, UserRole
from repositories.application_repository import ApplicationRepository
from schemas.application_schema import ApplicationCreateRequest, ApplicationStatusEnum


class ApplicationAlreadyExistsError(Exception):
    pass


class ApplicationNotFoundError(Exception):
    pass


class InternshipNotFoundError(Exception):
    pass


class ForbiddenApplicationAccessError(Exception):
    pass


class InvalidStatusTransitionError(Exception):
    pass


class MissingResumeError(Exception):
    pass


class ResumeNotFoundError(Exception):
    pass


class ApplicationService:
    _allowed_status_transitions: dict[ApplicationStatus, set[ApplicationStatus]] = {
        ApplicationStatus.APPLIED: {
            ApplicationStatus.UNDER_REVIEW,
            ApplicationStatus.REJECTED,
        },
        ApplicationStatus.UNDER_REVIEW: {
            ApplicationStatus.SHORTLISTED,
            ApplicationStatus.SELECTED,
            ApplicationStatus.REJECTED,
        },
        ApplicationStatus.SHORTLISTED: {
            ApplicationStatus.SELECTED,
            ApplicationStatus.REJECTED,
        },
        ApplicationStatus.SELECTED: {
            ApplicationStatus.IN_PROGRESS,
            ApplicationStatus.COMPLETED,
            ApplicationStatus.REJECTED,
        },
        ApplicationStatus.IN_PROGRESS: {
            ApplicationStatus.COMPLETED,
            ApplicationStatus.REJECTED,
        },
        ApplicationStatus.REJECTED: set(),
        ApplicationStatus.COMPLETED: set(),
    }

    def __init__(self, application_repository: ApplicationRepository):
        self.application_repository = application_repository
        self.resume_dir = Path("uploads") / "resumes"

    def apply(self, payload: ApplicationCreateRequest, current_user: User) -> Application:
        if not current_user.resume_url:
            raise MissingResumeError("Please upload your resume before applying")

        if not self.application_repository.internship_exists(payload.internship_id):
            raise InternshipNotFoundError("Internship not found")

        existing = self.application_repository.get_by_user_and_internship(
            current_user.id,
            payload.internship_id,
        )
        if existing is not None:
            raise ApplicationAlreadyExistsError(
                "You have already applied for this internship"
            )

        try:
            return self.application_repository.create(
                user_id=current_user.id,
                internship_id=payload.internship_id,
                resume_url=current_user.resume_url,
            )
        except IntegrityError as exc:
            self.application_repository.db.rollback()
            raise ApplicationAlreadyExistsError(
                "You have already applied for this internship"
            ) from exc

    def get_my_applications(self, current_user: User) -> list[Application]:
        return self.application_repository.get_by_user(current_user.id)

    def get_my_applications_with_internship(
        self,
        current_user: User,
    ) -> list[tuple[Application, Internship]]:
        return self.application_repository.list_by_user_with_internship(current_user.id)

    def get_application_detail(
        self,
        application_id: int,
        current_user: User,
    ) -> tuple[Application, User, Internship]:
        result = self.application_repository.get_application_with_user_and_internship(
            application_id
        )
        if result is None:
            raise ApplicationNotFoundError("Application not found")

        application, student, internship = result

        if current_user.role == UserRole.admin:
            return application, student, internship

        if current_user.role == UserRole.student:
            if application.user_id != current_user.id:
                raise ForbiddenApplicationAccessError("You cannot access this application")
            return application, student, internship

        if current_user.role == UserRole.company:
            if internship.created_by != current_user.id:
                raise ForbiddenApplicationAccessError("You cannot access this application")
            return application, student, internship

        raise ForbiddenApplicationAccessError("You cannot access this application")

    def get_company_applicants(
        self,
        internship_id: int,
        current_user: User,
    ) -> list[tuple[Application, User]]:
        internship = self.application_repository.get_internship_by_id(internship_id)
        if internship is None:
            raise InternshipNotFoundError("Internship not found")

        if current_user.role != UserRole.admin and internship.created_by != current_user.id:
            raise ForbiddenApplicationAccessError("You cannot access these applicants")

        return self.application_repository.list_by_internship_with_user(internship_id)

    def update_application_status(
        self,
        application_id: int,
        new_status: ApplicationStatusEnum,
        current_user: User,
    ) -> Application:
        result = self.application_repository.get_application_with_internship(application_id)
        if result is None:
            raise ApplicationNotFoundError("Application not found")

        application, internship = result
        if current_user.role == UserRole.student:
            raise ForbiddenApplicationAccessError("You cannot update this application")

        if current_user.role == UserRole.company and internship.created_by != current_user.id:
            raise ForbiddenApplicationAccessError("You cannot update this application")

        target_status = ApplicationStatus(new_status.value)

        if application.status == target_status:
            raise InvalidStatusTransitionError(
                f"Application is already in status {target_status.value}"
            )

        allowed_next = self._allowed_status_transitions.get(application.status, set())
        print(f"DEBUG: Status update for App {application_id}")
        print(f"DEBUG: Current: {application.status}, Target: {target_status}, Allowed: {allowed_next}")
        
        if target_status not in allowed_next:
            raise InvalidStatusTransitionError(
                "Invalid status transition "
                f"from {application.status.value} to {target_status.value}"
            )

        return self.application_repository.update_status(application, target_status)

    def get_application_resume_url(
        self,
        application_id: int,
        current_user: User,
    ) -> str:
        result = self.application_repository.get_application_with_internship(application_id)
        if result is None:
            raise ApplicationNotFoundError("Application not found")

        application, internship = result

        if current_user.role == UserRole.student and application.user_id != current_user.id:
            raise ForbiddenApplicationAccessError("You cannot access this resume")

        if current_user.role == UserRole.company and internship.created_by != current_user.id:
            raise ForbiddenApplicationAccessError("You cannot access this resume")

        resume_url = application.resume_url
        if not resume_url:
            raise ResumeNotFoundError("Resume not available for this application")

        return resume_url

    def _get_application_or_raise(self, application_id: int) -> Application:
        application = self.application_repository.get_by_id(application_id)
        if application is None:
            raise ApplicationNotFoundError("Application not found")
        return application