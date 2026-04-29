import secrets
from datetime import datetime, timedelta, timezone

from core.config import settings
from core.security import create_access_token, hash_password, verify_password
from models.user_model import User, UserRole
from repositories.user_repository import UserRepository
from schemas.auth_schema import (
    CompanySignupRequest,
    LoginOTPRequest,
    LoginRequest,
    ResetPasswordRequest,
    SendOTPRequest,
    SignupRequest,
    TokenResponse,
    UserResponse,
    VerifyOTPRequest,
)
from utils.email_utils import send_otp_email


class UserAlreadyExistsError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class InvalidOTPError(Exception):
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

    def send_otp(self, payload: SendOTPRequest) -> None:
        normalized_email = payload.email.lower()
        user = self.user_repository.get_by_email(normalized_email)
        if user is None:
            raise UserNotFoundError("User with this email does not exist")

        otp = "".join([str(secrets.randbelow(10)) for _ in range(6)])
        otp_hash = hash_password(otp)
        expiry = datetime.now(timezone.utc) + timedelta(minutes=5)

        self.user_repository.set_otp(user, otp_hash=otp_hash, expiry=expiry)
        send_otp_email(normalized_email, otp)

    def verify_otp(self, payload: VerifyOTPRequest) -> None:
        normalized_email = payload.email.lower()
        user = self.user_repository.get_by_email(normalized_email)
        if user is None:
            raise UserNotFoundError("User with this email does not exist")

        if user.otp_hash is None or user.otp_expiry is None:
            raise InvalidOTPError("OTP not sent or expired")

        if datetime.now(timezone.utc) > user.otp_expiry:
            raise InvalidOTPError("OTP has expired")

        if not verify_password(payload.otp, user.otp_hash):
            raise InvalidOTPError("Invalid OTP")

    def reset_password(self, payload: ResetPasswordRequest) -> None:
        self.verify_otp(VerifyOTPRequest(email=payload.email, otp=payload.otp))

        normalized_email = payload.email.lower()
        user = self.user_repository.get_by_email(normalized_email)

        password_hash = hash_password(payload.new_password)
        self.user_repository.update_password(user, password_hash=password_hash)
        self.user_repository.clear_otp(user)

    def login_otp(self, payload: LoginOTPRequest) -> TokenResponse:
        self.verify_otp(VerifyOTPRequest(email=payload.email, otp=payload.otp))

        normalized_email = payload.email.lower()
        user = self.user_repository.get_by_email(normalized_email)

        self.user_repository.clear_otp(user)

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
