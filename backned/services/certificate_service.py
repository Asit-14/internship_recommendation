from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from models.application_model import ApplicationStatus
from models.certificate_model import Certificate
from models.user_model import User, UserRole
from repositories.certificate_repository import CertificateRepository
from schemas.certificate_schema import CertificateGenerateRequest, CertificateResponse
from utils.pdf_generator import generate_certificate_pdf
from core.config import settings
import cloudinary
import cloudinary.uploader


class CertificateNotFoundError(Exception):
    pass


class CertificatePermissionDeniedError(Exception):
    pass


class CertificateValidationError(Exception):
    pass


class CertificateConflictError(Exception):
    pass


class CertificateService:
    def __init__(
        self,
        certificate_repository: CertificateRepository,
        *,
        certificates_dir: Path | None = None,
    ):
        self.certificate_repository = certificate_repository
        self.certificates_dir = certificates_dir or Path("generated_certificates")

    def generate_certificate(
        self,
        payload: CertificateGenerateRequest,
        *,
        generated_by: User,
    ) -> CertificateResponse:
        # Permission check: admin or company owner
        application = self.certificate_repository.get_application_by_id(
            payload.application_id
        )
        if application is None:
            raise CertificateNotFoundError("Application not found")

        internship = self.certificate_repository.get_internship_by_id(
            application.internship_id
        )
        if internship is None:
            raise CertificateNotFoundError("Internship not found")

        if generated_by.role == UserRole.company:
            if internship.created_by != generated_by.id:
                raise CertificatePermissionDeniedError(
                    "Only the company that posted the internship can generate this certificate"
                )
        elif generated_by.role == UserRole.student:
            if application.user_id != generated_by.id:
                raise CertificatePermissionDeniedError(
                    "You can only generate your own certificate"
                )
        elif generated_by.role != UserRole.admin:
            raise CertificatePermissionDeniedError(
                "Only admin, company, or the student themselves can generate certificates"
            )
        if application.status != ApplicationStatus.COMPLETED:
            raise CertificateValidationError(
                "Certificate can only be generated after internship completion"
            )

        existing = self.certificate_repository.get_by_user_and_internship(
            user_id=application.user_id,
            internship_id=application.internship_id,
        )
        if existing is not None:
            raise CertificateConflictError(
                "Certificate already exists for this internship"
            )

        user = self.certificate_repository.get_user_by_id(application.user_id)
        if user is None:
            raise CertificateNotFoundError("User not found")

        certificate_id = self._generate_unique_certificate_id()
        user_name = self._format_user_name(user)

        file_path = generate_certificate_pdf(
            user_name=user_name,
            internship_title=internship.title,
            duration_weeks=internship.duration,
            skills_acquired=internship.skills_required,
            certificate_id=certificate_id,
            output_dir=self.certificates_dir,
        )

        if not settings.cloudinary_cloud_name:
            raise CertificateValidationError("Cloudinary configuration is missing")

        cloudinary.config(
            cloud_name=settings.cloudinary_cloud_name,
            api_key=settings.cloudinary_api_key,
            api_secret=settings.cloudinary_api_secret,
            secure=True,
        )

        try:
            upload_result = cloudinary.uploader.upload(
                str(file_path),
                public_id=certificate_id,
                folder="certificates",
                resource_type="raw",
            )
            certificate_url = upload_result.get("secure_url")
        except Exception as e:
            raise CertificateValidationError(f"Failed to upload certificate: {str(e)}")
        finally:
            file_path.unlink(missing_ok=True)

        certificate = self.certificate_repository.create(
            certificate_data={
                "user_id": application.user_id,
                "internship_id": application.internship_id,
                "certificate_id": certificate_id,
                "certificate_url": certificate_url,
            }
        )
        return CertificateResponse.model_validate(certificate)

    def get_my_certificates(self, *, current_user: User) -> list[CertificateResponse]:
        certificates = self.certificate_repository.get_all_by_user(current_user.id)
        return [CertificateResponse.model_validate(c) for c in certificates]

    def get_certificate(
        self,
        certificate_db_id: int,
        *,
        current_user: User,
    ) -> Certificate:
        certificate = self.certificate_repository.get_by_id(certificate_db_id)
        if certificate is None:
            raise CertificateNotFoundError("Certificate not found")

        if (
            current_user.role == UserRole.student
            and certificate.user_id != current_user.id
        ):
            raise CertificatePermissionDeniedError(
                "You can only download your own certificate"
            )

        return certificate

    def get_certificate_by_id(self, certificate_id: str) -> CertificateResponse:
        certificate = self.certificate_repository.get_by_certificate_id(certificate_id)
        if certificate is None:
            raise CertificateNotFoundError(
                f"Certificate with ID {certificate_id} not found"
            )

        return CertificateResponse.model_validate(certificate)

    def _generate_unique_certificate_id(self) -> str:
        for _ in range(10):
            stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
            candidate = f"CERT-{stamp}-{uuid4().hex[:8].upper()}"
            if self.certificate_repository.get_by_certificate_id(candidate) is None:
                return candidate

        raise CertificateValidationError("Could not generate a unique certificate ID")

    @staticmethod
    def _format_user_name(user: User) -> str:
        if user.name and user.name.strip():
            return user.name.strip()

        local_part = user.email.split("@", maxsplit=1)[0]
        spaced = local_part.replace(".", " ").replace("_", " ").replace("-", " ")
        pieces = [part.capitalize() for part in spaced.split() if part]
        return " ".join(pieces) if pieces else user.email
