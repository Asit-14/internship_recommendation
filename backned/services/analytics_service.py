from analytics.analytics_schema import (
    AdminOverviewResponse,
    ApplicationsAnalyticsResponse,
    CombinedMonthlyTrendPoint,
    DashboardAnalyticsResponse,
    DashboardCharts,
    DashboardSummary,
    DualSeriesChart,
    InternshipsAnalyticsResponse,
    MonthlyCountPoint,
    SectorDistributionPoint,
    SingleSeriesChart,
    StatusDistributionPoint,
    UsersAnalyticsResponse,
)
from repositories.analytics_repository import AnalyticsRepository


class AnalyticsService:
    ACTIVE_USER_WINDOW_DAYS = 30
    DEFAULT_TREND_MONTHS = 12

    def __init__(self, analytics_repository: AnalyticsRepository):
        self.analytics_repository = analytics_repository

    def get_dashboard_analytics(self) -> DashboardAnalyticsResponse:
        user_counts = self.analytics_repository.get_user_counts(
            active_window_days=self.ACTIVE_USER_WINDOW_DAYS
        )
        internship_counts = self.analytics_repository.get_internship_counts()
        application_counts = self.analytics_repository.get_application_counts()
        certificates_issued = self.analytics_repository.get_certificate_count()

        sector_distribution_raw = self.analytics_repository.get_sector_distribution()
        user_trends_raw = self.analytics_repository.get_monthly_user_trends(
            months=self.DEFAULT_TREND_MONTHS
        )
        application_trends_raw = self.analytics_repository.get_monthly_application_trends(
            months=self.DEFAULT_TREND_MONTHS
        )
        combined_monthly_trends_raw = self._combine_monthly_trends(
            user_trends_raw,
            application_trends_raw,
        )

        summary = DashboardSummary(
            total_users=user_counts["total_users"],
            active_users=user_counts["active_users"],
            total_internships=internship_counts["total_internships"],
            active_internships=internship_counts["active_internships"],
            total_applications=application_counts["total_applications"],
            application_success_rate=application_counts["application_success_rate"],
            completed_internships=internship_counts["completed_internships"],
            certificates_issued=certificates_issued,
        )

        sector_distribution = [
            SectorDistributionPoint(**item)
            for item in sector_distribution_raw
        ]
        combined_monthly_trends = [
            CombinedMonthlyTrendPoint(**item)
            for item in combined_monthly_trends_raw
        ]

        return DashboardAnalyticsResponse(
            summary=summary,
            sector_distribution=sector_distribution,
            monthly_trends=combined_monthly_trends,
            charts=DashboardCharts(
                sector_distribution=self._build_single_series_chart(
                    items=sector_distribution_raw,
                    label_key="sector",
                ),
                monthly_trends=self._build_dual_series_chart(combined_monthly_trends_raw),
            ),
        )

    def get_users_analytics(self) -> UsersAnalyticsResponse:
        user_counts = self.analytics_repository.get_user_counts(
            active_window_days=self.ACTIVE_USER_WINDOW_DAYS
        )
        monthly_trends_raw = self.analytics_repository.get_monthly_user_trends(
            months=self.DEFAULT_TREND_MONTHS
        )

        total_users = user_counts["total_users"]
        active_users = user_counts["active_users"]
        active_user_rate = round((active_users / total_users) * 100, 2) if total_users else 0.0

        return UsersAnalyticsResponse(
            total_users=total_users,
            active_users=active_users,
            active_user_rate=active_user_rate,
            monthly_trends=[MonthlyCountPoint(**item) for item in monthly_trends_raw],
            chart=self._build_single_series_chart(
                items=monthly_trends_raw,
                label_key="month",
            ),
        )

    def get_admin_overview(self) -> AdminOverviewResponse:
        role_counts = self.analytics_repository.get_user_role_counts()
        internship_counts = self.analytics_repository.get_internship_counts()
        application_counts = self.analytics_repository.get_application_counts()

        user_trends_raw = self.analytics_repository.get_monthly_user_trends(
            months=self.DEFAULT_TREND_MONTHS
        )
        application_trends_raw = self.analytics_repository.get_monthly_application_trends(
            months=self.DEFAULT_TREND_MONTHS
        )
        combined_monthly_trends_raw = self._combine_monthly_trends(
            user_trends_raw,
            application_trends_raw,
        )

        sector_distribution_raw = self.analytics_repository.get_sector_distribution()

        total_students = role_counts.get("student", 0)
        total_companies = role_counts.get("company", 0)
        total_admins = role_counts.get("admin", 0)
        total_users = total_students + total_companies + total_admins

        return AdminOverviewResponse(
            total_users=total_users,
            total_students=total_students,
            total_companies=total_companies,
            total_internships=internship_counts["total_internships"],
            total_applications=application_counts["total_applications"],
            success_rate=application_counts["application_success_rate"],
            monthly_stats=[
                CombinedMonthlyTrendPoint(**item) for item in combined_monthly_trends_raw
            ],
            sector_distribution=[
                SectorDistributionPoint(**item) for item in sector_distribution_raw
            ],
        )

    def get_internships_analytics(self) -> InternshipsAnalyticsResponse:
        internship_counts = self.analytics_repository.get_internship_counts()
        sector_distribution_raw = self.analytics_repository.get_sector_distribution()

        return InternshipsAnalyticsResponse(
            total_internships=internship_counts["total_internships"],
            active_internships=internship_counts["active_internships"],
            completed_internships=internship_counts["completed_internships"],
            sector_distribution=[
                SectorDistributionPoint(**item) for item in sector_distribution_raw
            ],
            chart=self._build_single_series_chart(
                items=sector_distribution_raw,
                label_key="sector",
            ),
        )

    def get_applications_analytics(self) -> ApplicationsAnalyticsResponse:
        application_counts = self.analytics_repository.get_application_counts()
        monthly_trends_raw = self.analytics_repository.get_monthly_application_trends(
            months=self.DEFAULT_TREND_MONTHS
        )
        status_distribution_raw = self.analytics_repository.get_application_status_distribution()

        return ApplicationsAnalyticsResponse(
            total_applications=application_counts["total_applications"],
            successful_applications=application_counts["successful_applications"],
            application_success_rate=application_counts["application_success_rate"],
            status_distribution=[
                StatusDistributionPoint(**item) for item in status_distribution_raw
            ],
            monthly_trends=[MonthlyCountPoint(**item) for item in monthly_trends_raw],
            status_chart=self._build_single_series_chart(
                items=status_distribution_raw,
                label_key="status",
            ),
            monthly_chart=self._build_single_series_chart(
                items=monthly_trends_raw,
                label_key="month",
            ),
        )

    @staticmethod
    def _build_single_series_chart(
        *,
        items: list[dict[str, int | str]],
        label_key: str,
        value_key: str = "count",
    ) -> SingleSeriesChart:
        labels = [str(item[label_key]) for item in items]
        values = [int(item[value_key]) for item in items]
        return SingleSeriesChart(labels=labels, values=values)

    @staticmethod
    def _build_dual_series_chart(items: list[dict[str, int | str]]) -> DualSeriesChart:
        labels = [str(item["month"]) for item in items]
        users = [int(item["users"]) for item in items]
        applications = [int(item["applications"]) for item in items]
        return DualSeriesChart(labels=labels, users=users, applications=applications)

    @staticmethod
    def _combine_monthly_trends(
        user_trends: list[dict[str, int | str]],
        application_trends: list[dict[str, int | str]],
    ) -> list[dict[str, int | str]]:
        users_by_month = {str(item["month"]): int(item["count"]) for item in user_trends}
        applications_by_month = {
            str(item["month"]): int(item["count"]) for item in application_trends
        }

        all_months = sorted(set(users_by_month).union(applications_by_month))
        return [
            {
                "month": month,
                "users": users_by_month.get(month, 0),
                "applications": applications_by_month.get(month, 0),
            }
            for month in all_months
        ]
