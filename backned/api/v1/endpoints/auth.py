from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from repositories.user_repository import UserRepository
from schemas.auth_schema import (
    CompanySignupRequest,
    LoginRequest,
    SignupRequest,
    TokenResponse,
    UserResponse,
)
from services.auth_service import AuthService, InvalidCredentialsError, UserAlreadyExistsError


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
