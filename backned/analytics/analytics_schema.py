from pydantic import BaseModel, Field


class SingleSeriesChart(BaseModel):
    labels: list[str] = Field(default_factory=list)
    values: list[int] = Field(default_factory=list)


class DualSeriesChart(BaseModel):
    labels: list[str] = Field(default_factory=list)
    users: list[int] = Field(default_factory=list)
    applications: list[int] = Field(default_factory=list)


class MonthlyCountPoint(BaseModel):
    month: str
    count: int = Field(ge=0)


class CombinedMonthlyTrendPoint(BaseModel):
    month: str
    users: int = Field(ge=0)
    applications: int = Field(ge=0)


class SectorDistributionPoint(BaseModel):
    sector: str
    count: int = Field(ge=0)


class StatusDistributionPoint(BaseModel):
    status: str
    count: int = Field(ge=0)


class DashboardSummary(BaseModel):
    total_users: int = Field(ge=0)
    active_users: int = Field(ge=0)
    total_internships: int = Field(ge=0)
    active_internships: int = Field(ge=0)
    total_applications: int = Field(ge=0)
    application_success_rate: float = Field(ge=0, le=100)
    completed_internships: int = Field(ge=0)
    certificates_issued: int = Field(ge=0)


class DashboardCharts(BaseModel):
    sector_distribution: SingleSeriesChart
    monthly_trends: DualSeriesChart


class DashboardAnalyticsResponse(BaseModel):
    summary: DashboardSummary
    sector_distribution: list[SectorDistributionPoint] = Field(default_factory=list)
    monthly_trends: list[CombinedMonthlyTrendPoint] = Field(default_factory=list)
    charts: DashboardCharts


class AdminOverviewResponse(BaseModel):
    total_users: int = Field(ge=0)
    total_students: int = Field(ge=0)
    total_companies: int = Field(ge=0)
    total_internships: int = Field(ge=0)
    total_applications: int = Field(ge=0)
    success_rate: float = Field(ge=0, le=100)
    monthly_stats: list[CombinedMonthlyTrendPoint] = Field(default_factory=list)
    sector_distribution: list[SectorDistributionPoint] = Field(default_factory=list)


class UsersAnalyticsResponse(BaseModel):
    total_users: int = Field(ge=0)
    active_users: int = Field(ge=0)
    active_user_rate: float = Field(ge=0, le=100)
    monthly_trends: list[MonthlyCountPoint] = Field(default_factory=list)
    chart: SingleSeriesChart


class InternshipsAnalyticsResponse(BaseModel):
    total_internships: int = Field(ge=0)
    active_internships: int = Field(ge=0)
    completed_internships: int = Field(ge=0)
    sector_distribution: list[SectorDistributionPoint] = Field(default_factory=list)
    chart: SingleSeriesChart


class ApplicationsAnalyticsResponse(BaseModel):
    total_applications: int = Field(ge=0)
    successful_applications: int = Field(ge=0)
    application_success_rate: float = Field(ge=0, le=100)
    status_distribution: list[StatusDistributionPoint] = Field(default_factory=list)
    monthly_trends: list[MonthlyCountPoint] = Field(default_factory=list)
    status_chart: SingleSeriesChart
    monthly_chart: SingleSeriesChart
