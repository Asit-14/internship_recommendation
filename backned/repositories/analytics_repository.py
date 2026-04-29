from datetime import datetime, timedelta, timezone

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from models.application_model import Application, ApplicationStatus
from models.certificate_model import Certificate
from models.internship_model import Internship
from models.user_model import User


class AnalyticsRepository:
    SUCCESSFUL_APPLICATION_STATUSES = (
        ApplicationStatus.SELECTED,
        ApplicationStatus.IN_PROGRESS,
        ApplicationStatus.COMPLETED,
    )

    def __init__(self, db: Session):
        self.db = db

    def get_user_counts(self, *, active_window_days: int = 30) -> dict[str, int]:
        active_cutoff = datetime.now(timezone.utc) - timedelta(days=active_window_days)

        active_users_subquery = (
            self.db.query(func.count(func.distinct(Application.user_id)))
            .filter(Application.applied_at >= active_cutoff)
            .scalar_subquery()
        )

        counts = self.db.query(
            func.count(User.id).label("total_users"),
            active_users_subquery.label("active_users"),
        ).one()

        return {
            "total_users": int(counts.total_users or 0),
            "active_users": int(counts.active_users or 0),
        }

    def get_user_role_counts(self) -> dict[str, int]:
        rows = (
            self.db.query(User.role.label("role"), func.count(User.id).label("count"))
            .group_by(User.role)
            .all()
        )

        counts: dict[str, int] = {}
        for row in rows:
            role_value = row.role.value if hasattr(row.role, "value") else str(row.role)
            counts[role_value] = int(row.count)

        return counts

    def get_internship_counts(self) -> dict[str, int]:
        completed_subquery = (
            self.db.query(func.count(Application.id))
            .filter(Application.status == ApplicationStatus.COMPLETED)
            .scalar_subquery()
        )

        counts = self.db.query(
            func.count(Internship.id).label("total_internships"),
            func.coalesce(
                func.sum(case((Internship.is_active.is_(True), 1), else_=0)),
                0,
            ).label("active_internships"),
            completed_subquery.label("completed_internships"),
        ).one()

        return {
            "total_internships": int(counts.total_internships or 0),
            "active_internships": int(counts.active_internships or 0),
            "completed_internships": int(counts.completed_internships or 0),
        }

    def get_application_counts(self) -> dict[str, int | float]:
        counts = self.db.query(
            func.count(Application.id).label("total_applications"),
            func.coalesce(
                func.sum(
                    case(
                        (Application.status.in_(self.SUCCESSFUL_APPLICATION_STATUSES), 1),
                        else_=0,
                    )
                ),
                0,
            ).label("successful_applications"),
        ).one()

        total_applications = int(counts.total_applications or 0)
        successful_applications = int(counts.successful_applications or 0)
        success_rate = round((successful_applications / total_applications) * 100, 2) if total_applications else 0.0

        return {
            "total_applications": total_applications,
            "successful_applications": successful_applications,
            "application_success_rate": success_rate,
        }

    def get_certificate_count(self) -> int:
        total = self.db.query(func.count(Certificate.id)).scalar()
        return int(total or 0)

    def get_sector_distribution(self) -> list[dict[str, int | str]]:
        rows = (
            self.db.query(
                Internship.sector.label("sector"),
                func.count(Internship.id).label("count"),
            )
            .group_by(Internship.sector)
            .order_by(func.count(Internship.id).desc(), Internship.sector.asc())
            .all()
        )

        return [
            {
                "sector": str(row.sector),
                "count": int(row.count),
            }
            for row in rows
        ]

    def get_application_status_distribution(self) -> list[dict[str, int | str]]:
        rows = (
            self.db.query(
                Application.status.label("status"),
                func.count(Application.id).label("count"),
            )
            .group_by(Application.status)
            .order_by(Application.status.asc())
            .all()
        )

        distribution: list[dict[str, int | str]] = []
        for row in rows:
            status_value = row.status.value if isinstance(row.status, ApplicationStatus) else str(row.status)
            distribution.append(
                {
                    "status": status_value,
                    "count": int(row.count),
                }
            )

        return distribution

    def get_monthly_user_trends(self, *, months: int = 12) -> list[dict[str, int | str]]:
        return self._get_monthly_counts(
            model_id_column=User.id,
            datetime_column=User.created_at,
            months=months,
        )

    def get_monthly_application_trends(self, *, months: int = 12) -> list[dict[str, int | str]]:
        return self._get_monthly_counts(
            model_id_column=Application.id,
            datetime_column=Application.applied_at,
            months=months,
        )

    def _get_monthly_counts(
        self,
        *,
        model_id_column,
        datetime_column,
        months: int,
    ) -> list[dict[str, int | str]]:
        labels = self._generate_month_labels(months)
        first_year, first_month = labels[0].split("-")
        start_date = datetime(int(first_year), int(first_month), 1)

        month_bucket = self._month_bucket_expression(datetime_column)

        rows = (
            self.db.query(
                month_bucket.label("month"),
                func.count(model_id_column).label("count"),
            )
            .filter(datetime_column >= start_date)
            .group_by(month_bucket)
            .order_by(month_bucket)
            .all()
        )

        counts_by_month = {str(row.month): int(row.count) for row in rows}
        return [{"month": label, "count": counts_by_month.get(label, 0)} for label in labels]

    def _month_bucket_expression(self, datetime_column):
        dialect_name = self.db.bind.dialect.name if self.db.bind is not None else ""

        if dialect_name == "sqlite":
            return func.strftime("%Y-%m", datetime_column)

        if dialect_name in {"mysql", "mariadb"}:
            return func.date_format(datetime_column, "%Y-%m")

        return func.to_char(func.date_trunc("month", datetime_column), "YYYY-MM")

    @staticmethod
    def _generate_month_labels(months: int) -> list[str]:
        normalized_months = max(1, months)
        now = datetime.now(timezone.utc)
        current_index = now.year * 12 + (now.month - 1)

        labels: list[str] = []
        for offset in range(normalized_months - 1, -1, -1):
            month_index = current_index - offset
            year, month_zero_based = divmod(month_index, 12)
            labels.append(f"{year:04d}-{month_zero_based + 1:02d}")

        return labels
