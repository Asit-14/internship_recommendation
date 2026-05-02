from datetime import datetime, timezone
from sqlalchemy.orm import Session

from models.user_model import User, UserRole


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).one_or_none()

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).one_or_none()

    def list_non_admin(self) -> list[User]:
        return (
            self.db.query(User)
            .filter(User.role != UserRole.admin)
            .order_by(User.created_at.desc())
            .all()
        )

    def list_by_role(self, role: UserRole) -> list[User]:
        return (
            self.db.query(User)
            .filter(User.role == role)
            .order_by(User.created_at.desc())
            .all()
        )

    def create(
        self,
        *,
        name: str,
        email: str,
        password_hash: str,
        role: UserRole,
        is_verified: bool,
    ) -> User:
        user = User(
            name=name,
            email=email,
            password_hash=password_hash,
            role=role,
            is_verified=is_verified,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def set_verified(self, user: User, *, is_verified: bool) -> User:
        user.is_verified = is_verified
        self.db.commit()
        self.db.refresh(user)
        return user

    def set_role(
        self,
        user: User,
        *,
        role: UserRole,
        is_verified: bool | None = None,
    ) -> User:
        user.role = role
        if is_verified is not None:
            user.is_verified = is_verified
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_profile(self, user: User, *, updates: dict) -> User:
        for field, value in updates.items():
            setattr(user, field, value)

        self.db.commit()
        self.db.refresh(user)
        return user

    def set_resume_url(self, user: User, *, resume_url: str) -> User:
        user.resume_url = resume_url
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()

    def set_otp(self, user: User, *, otp_hash: str, expiry: datetime) -> User:
        user.otp_hash = otp_hash
        user.otp_expiry = expiry
        self.db.commit()
        self.db.refresh(user)
        return user

    def clear_otp(self, user: User) -> User:
        user.otp_hash = None
        user.otp_expiry = None
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_password(self, user: User, *, password_hash: str) -> User:
        user.password_hash = password_hash
        self.db.commit()
        self.db.refresh(user)
        return user

    def soft_delete(self, user: User) -> User:
        user.is_active = False
        user.deleted_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(user)
        return user
