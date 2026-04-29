from datetime import timedelta

from core.config import settings
from core.security import create_access_token, hash_password, verify_password
from models.user_model import User, UserRole
from repositories.user_repository import UserRepository
from schemas.auth_schema import (
    CompanySignupRequest,
    LoginRequest,
    SignupRequest,
    TokenResponse,
    UserResponse,
)


class UserAlreadyExistsError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class AuthService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def signup(self, payload: SignupRequest) -> User:
        normalized_name = " ".join(payload.name.split())
        normalized_email = payload.email.lower()

        existing_user = self.user_repository.get_by_email(normalized_email)
        if existing_user is not None:
            raise UserAlreadyExistsError("User with this email already exists")

        password_hash = hash_password(payload.password)

        return self.user_repository.create(
            name=normalized_name,
            email=normalized_email,
            password_hash=password_hash,
            role=UserRole.student,
            is_verified=True,
        )

    def register_company(self, payload: CompanySignupRequest) -> User:
        normalized_name = " ".join(payload.company_name.split())
        normalized_email = payload.email.lower()

        existing_user = self.user_repository.get_by_email(normalized_email)
        if existing_user is not None:
            raise UserAlreadyExistsError("User with this email already exists")

        password_hash = hash_password(payload.password)

        return self.user_repository.create(
            name=normalized_name,
            email=normalized_email,
            password_hash=password_hash,
            role=UserRole.company,
            is_verified=False,
        )

    def ensure_admin_user(self, *, name: str, email: str, password: str) -> User:
        normalized_name = " ".join(name.split()) or "Admin"
        normalized_email = email.lower()

        existing_user = self.user_repository.get_by_email(normalized_email)
        if existing_user is not None:
            if existing_user.role != UserRole.admin:
                return self.user_repository.set_role(
                    existing_user,
                    role=UserRole.admin,
                    is_verified=True,
                )
            return existing_user

        password_hash = hash_password(password)

        return self.user_repository.create(
            name=normalized_name,
            email=normalized_email,
            password_hash=password_hash,
            role=UserRole.admin,
            is_verified=True,
        )

    def login(self, payload: LoginRequest) -> TokenResponse:
        normalized_email = payload.email.lower()
        user = self.user_repository.get_by_email(normalized_email)

        if user is None or not verify_password(payload.password, user.password_hash):
            raise InvalidCredentialsError("Invalid email or password")

        expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
        token = create_access_token(
            user_id=user.id,
            role=user.role,
            is_verified=user.is_verified,
            expires_delta=expires_delta,
        )

        return TokenResponse(
            access_token=token,
            expires_in=int(expires_delta.total_seconds()),
            user=UserResponse.model_validate(user),
        )
