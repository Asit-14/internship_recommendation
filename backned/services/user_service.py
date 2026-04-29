from datetime import datetime, timezone
from pathlib import Path

from fastapi import UploadFile

from models.user_model import User
from repositories.user_repository import UserRepository
from schemas.user_schema import ResumeUploadResponse, UserProfileUpdateRequest


class EmptyProfileUpdateError(Exception):
    pass


class InvalidResumeFileError(Exception):
    pass


class UserService:
    _allowed_resume_extensions = {".pdf", ".docx"}
    _max_resume_size_bytes = 5 * 1024 * 1024

    def __init__(self, user_repository: UserRepository, upload_dir: Path | None = None):
        self.user_repository = user_repository
        self.upload_dir = upload_dir or (Path("uploads") / "resumes")

    def get_profile(self, current_user: User) -> User:
        return current_user

    def update_profile(self, current_user: User, payload: UserProfileUpdateRequest) -> User:
        updates = payload.model_dump(exclude_unset=True)
        if not updates:
            raise EmptyProfileUpdateError("At least one profile field must be provided")

        if "skills" in updates and updates["skills"] is None:
            updates["skills"] = []

        return self.user_repository.update_profile(current_user, updates=updates)

    async def upload_resume(
        self,
        *,
        current_user: User,
        file: UploadFile,
    ) -> ResumeUploadResponse:
        original_name = file.filename or ""
        extension = Path(original_name).suffix.lower()

        if extension not in self._allowed_resume_extensions:
            raise InvalidResumeFileError("Only PDF and DOCX files are allowed")

        try:
            content = await file.read(self._max_resume_size_bytes + 1)
        finally:
            await file.close()

        file_size = len(content)
        if file_size == 0:
            raise InvalidResumeFileError("Uploaded file is empty")

        if file_size > self._max_resume_size_bytes:
            raise InvalidResumeFileError("Resume must be 5 MB or smaller")

        self.upload_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        stored_filename = f"user_{current_user.id}_{timestamp}{extension}"
        output_path = self.upload_dir / stored_filename
        output_path.write_bytes(content)

        self.user_repository.set_resume_filename(current_user, resume_filename=stored_filename)

        return ResumeUploadResponse(
            filename=stored_filename,
            content_type=file.content_type or "application/octet-stream",
            size_bytes=file_size,
            uploaded_at=datetime.now(timezone.utc),
        )
