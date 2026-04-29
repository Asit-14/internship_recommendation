from models.application_model import ApplicationStatus
from models.user_model import User, UserRole
from repositories.progress_repository import ProgressRepository
from schemas.progress_schema import ProgressCreate, ProgressResponse


class ProgressNotFoundError(Exception):
    pass


class ProgressPermissionDeniedError(Exception):
    pass


class ProgressValidationError(Exception):
    pass


class ProgressConflictError(Exception):
    pass


class ProgressService:
    def __init__(self, progress_repository: ProgressRepository):
        self.progress_repository = progress_repository

    def add_progress(self, payload: ProgressCreate, *, current_user: User) -> ProgressResponse:
        application = self.progress_repository.get_application_by_id(payload.application_id)
        if application is None:
            raise ProgressNotFoundError("Application not found")

        if current_user.role == UserRole.student and application.user_id != current_user.id:
            raise ProgressPermissionDeniedError("You can only update your own internship progress")

        internship = self.progress_repository.get_internship_by_id(application.internship_id)
        if internship is None:
            raise ProgressNotFoundError("Internship not found")

        if not internship.is_active:
            raise ProgressValidationError("Progress updates are allowed only for active internships")

        if payload.mentor_feedback is not None and current_user.role == UserRole.student:
            raise ProgressPermissionDeniedError("Students cannot add mentor feedback")

        existing_progress = self.progress_repository.get_by_application_and_week(
            application_id=payload.application_id,
            week_number=payload.week_number,
        )
        if existing_progress is not None:
            if current_user.role != UserRole.admin:
                raise ProgressConflictError("Progress for this week already exists")

            updates: dict[str, str] = {}
            if payload.work_done is not None:
                updates["work_done"] = payload.work_done
            if payload.mentor_feedback is not None:
                updates["mentor_feedback"] = payload.mentor_feedback

            if not updates:
                raise ProgressValidationError("At least one updatable field must be provided")

            updated = self.progress_repository.update(existing_progress, updates=updates)
            return ProgressResponse.model_validate(updated)

        if payload.work_done is None:
            raise ProgressValidationError("work_done is required for weekly progress updates")

        if payload.week_number > internship.duration:
            raise ProgressValidationError("week_number cannot exceed internship duration")

        if application.status in {
            ApplicationStatus.APPLIED,
            ApplicationStatus.UNDER_REVIEW,
            ApplicationStatus.SHORTLISTED,
            ApplicationStatus.REJECTED,
        }:
            raise ProgressValidationError("Internship is not active for progress updates")

        if application.status == ApplicationStatus.COMPLETED:
            raise ProgressValidationError("Internship has already been completed")

        application.status = self._next_status_for_progress(
            current_status=application.status,
            week_number=payload.week_number,
            internship_duration=internship.duration,
        )

        created = self.progress_repository.create(
            progress_data={
                "application_id": payload.application_id,
                "week_number": payload.week_number,
                "work_done": payload.work_done,
                "mentor_feedback": payload.mentor_feedback,
            }
        )
        return ProgressResponse.model_validate(created)

    def get_progress_logs(
        self,
        application_id: int,
        *,
        current_user: User,
    ) -> list[ProgressResponse]:
        application = self.progress_repository.get_application_by_id(application_id)
        if application is None:
            raise ProgressNotFoundError("Application not found")

        if current_user.role == UserRole.student and application.user_id != current_user.id:
            raise ProgressPermissionDeniedError("You can only view your own internship progress")

        logs = self.progress_repository.list_by_application(application_id=application_id)
        return [ProgressResponse.model_validate(log) for log in logs]

    @staticmethod
    def _next_status_for_progress(
        *,
        current_status: ApplicationStatus,
        week_number: int,
        internship_duration: int,
    ) -> ApplicationStatus:
        next_status = current_status

        if current_status == ApplicationStatus.SELECTED:
            next_status = ApplicationStatus.IN_PROGRESS

        if week_number >= internship_duration:
            next_status = ApplicationStatus.COMPLETED

        return next_status
