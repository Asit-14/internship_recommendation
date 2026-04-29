from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from models.application_model import ApplicationStatus
from models.certificate_model import Certificate
from models.user_model import User, UserRole
from repositories.certificate_repository import CertificateRepository
from schemas.certificate_schema import CertificateGenerateRequest, CertificateResponse
from utils.pdf_generator import generate_certificate_pdf


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
        if generated_by.role != UserRole.admin:
            raise CertificatePermissionDeniedError("Only admin users can generate certificates")

        application = self.certificate_repository.get_application_by_id(payload.application_id)
        if application is None:
            raise CertificateNotFoundError("Application not found")

        if application.status != ApplicationStatus.COMPLETED:
            raise CertificateValidationError(
                "Certificate can only be generated after internship completion"
            )

        existing = self.certificate_repository.get_by_user_and_internship(
            user_id=application.user_id,
            internship_id=application.internship_id,
        )
        if existing is not None:
            raise CertificateConflictError("Certificate already exists for this internship")

        user = self.certificate_repository.get_user_by_id(application.user_id)
        if user is None:
            raise CertificateNotFoundError("User not found")

        internship = self.certificate_repository.get_internship_by_id(application.internship_id)
        if internship is None:
            raise CertificateNotFoundError("Internship not found")

        certificate_id = self._generate_unique_certificate_id()
        user_name = self._format_user_name(user.email)

        file_path = generate_certificate_pdf(
            user_name=user_name,
            internship_title=internship.title,
            duration_weeks=internship.duration,
            certificate_id=certificate_id,
            output_dir=self.certificates_dir,
        )

        certificate = self.certificate_repository.create(
            certificate_data={
                "user_id": application.user_id,
                "internship_id": application.internship_id,
                "certificate_id": certificate_id,
                "certificate_url": file_path.as_posix(),
            }
        )
        return CertificateResponse.model_validate(certificate)

    def get_certificate_file(
        self,
        certificate_db_id: int,
        *,
        current_user: User,
    ) -> tuple[Certificate, Path]:
        certificate = self.certificate_repository.get_by_id(certificate_db_id)
        if certificate is None:
            raise CertificateNotFoundError("Certificate not found")

        if current_user.role == UserRole.student and certificate.user_id != current_user.id:
            raise CertificatePermissionDeniedError("You can only download your own certificate")

        file_path = Path(certificate.certificate_url)
        if not file_path.is_absolute():
            file_path = (Path.cwd() / file_path).resolve()

        if not file_path.exists():
            fallback = (self.certificates_dir / f"{certificate.certificate_id}.pdf").resolve()
            if fallback.exists():
                file_path = fallback
            else:
                raise CertificateNotFoundError("Certificate file not found")

        return certificate, file_path

    def _generate_unique_certificate_id(self) -> str:
        for _ in range(10):
            stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
            candidate = f"CERT-{stamp}-{uuid4().hex[:8].upper()}"
            if self.certificate_repository.get_by_certificate_id(candidate) is None:
                return candidate

        raise CertificateValidationError("Could not generate a unique certificate ID")

    @staticmethod
    def _format_user_name(email: str) -> str:
        local_part = email.split("@", maxsplit=1)[0]
        spaced = local_part.replace(".", " ").replace("_", " ").replace("-", " ")
        pieces = [part.capitalize() for part in spaced.split() if part]
        return " ".join(pieces) if pieces else email
