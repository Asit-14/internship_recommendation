from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from core.database import get_db
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
from services.auth_service import (
    AuthService,
    InvalidCredentialsError,
    InvalidOTPError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from utils.email_utils import send_otp_email


router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(UserRepository(db))


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest, service: AuthService = Depends(get_auth_service)) -> UserResponse:
    try:
        user = service.signup(payload)
    except UserAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return UserResponse.model_validate(user)


@router.post(
    "/register-company",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_company(
    payload: CompanySignupRequest,
    service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    try:
        user = service.register_company(payload)
    except UserAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login(payload: LoginRequest, service: AuthService = Depends(get_auth_service)) -> TokenResponse:
    try:
        return service.login(payload)
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


@router.post("/send-otp", status_code=status.HTTP_200_OK)
def send_otp(
    payload: SendOTPRequest,
    background_tasks: BackgroundTasks,
    service: AuthService = Depends(get_auth_service)
):
    try:
        otp = service.send_otp(payload)
        background_tasks.add_task(send_otp_email, payload.email, otp)
        return {"message": "OTP sent successfully"}
    except UserNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.post("/verify-otp", status_code=status.HTTP_200_OK)
def verify_otp(payload: VerifyOTPRequest, service: AuthService = Depends(get_auth_service)):
    try:
        service.verify_otp(payload)
        return {"message": "OTP verified successfully"}
    except (UserNotFoundError, InvalidOTPError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(payload: ResetPasswordRequest, service: AuthService = Depends(get_auth_service)):
    try:
        service.reset_password(payload)
        return {"message": "Password reset successfully"}
    except (UserNotFoundError, InvalidOTPError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/login-otp", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login_otp(payload: LoginOTPRequest, service: AuthService = Depends(get_auth_service)):
    try:
        return service.login_otp(payload)
    except (UserNotFoundError, InvalidOTPError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
