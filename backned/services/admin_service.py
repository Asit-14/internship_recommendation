from models.internship_model import Internship
from models.user_model import User, UserRole
from repositories.internship_repository import InternshipRepository
from repositories.user_repository import UserRepository


class CompanyNotFoundError(Exception):
    pass


class CompanyApprovalError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class AdminDeleteError(Exception):
    pass


class AdminInternshipNotFoundError(Exception):
    pass


class AdminService:
    def __init__(
        self,
        user_repository: UserRepository,
        internship_repository: InternshipRepository,
    ):
        self.user_repository = user_repository
        self.internship_repository = internship_repository

    def list_users(self) -> list[User]:
        return self.user_repository.list_non_admin()

    def list_companies(self) -> list[User]:
        return self.user_repository.list_by_role(UserRole.company)

    def approve_company(self, company_id: int) -> User:
        user = self.user_repository.get_by_id(company_id)
        if user is None:
            raise CompanyNotFoundError("Company not found")

        if user.role != UserRole.company:
            raise CompanyApprovalError("User is not a company account")

        if user.is_verified:
            return user

        return self.user_repository.set_verified(user, is_verified=True)

    def delete_user(self, user_id: int) -> None:
        user = self.user_repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError("User not found")

        if user.role == UserRole.admin:
            raise AdminDeleteError("Admin users cannot be deleted")

        self.user_repository.delete(user)

    def get_company_detail(self, company_id: int) -> tuple[User, list[Internship]]:
        user = self.user_repository.get_by_id(company_id)
        if user is None:
            raise CompanyNotFoundError("Company not found")

        if user.role != UserRole.company:
            raise CompanyApprovalError("User is not a company account")

        internships = self.internship_repository.list_by_creator(company_id)
        return user, internships

    def list_internships(self) -> list[Internship]:
        return self.internship_repository.list()

    def delete_internship(self, internship_id: int) -> None:
        internship = self.internship_repository.get_by_id(internship_id)
        if internship is None:
            raise AdminInternshipNotFoundError("Internship not found")

        self.internship_repository.delete(internship)
