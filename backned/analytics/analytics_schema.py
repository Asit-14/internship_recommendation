from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field, model_validator

# ---------------------------------------------------------------------------
# Shared type aliases
# ---------------------------------------------------------------------------

NonNegativeInt   = Annotated[int,   Field(ge=0)]
NonNegativeFloat = Annotated[float, Field(ge=0.0)]
Percentage       = Annotated[float, Field(ge=0.0, le=100.0)]
PositiveInt      = Annotated[int,   Field(gt=0)]

# Valid application status values — shared between point model and chart
ApplicationStatus = Literal[
    "pending",
    "under_review",
    "shortlisted",
    "accepted",
    "rejected",
    "withdrawn",
]


# ---------------------------------------------------------------------------
# Primitive chart series models
# ---------------------------------------------------------------------------

class SingleSeriesChart(BaseModel):
    """
    Serialised data for a single-dataset chart (bar, line, pie).

    ``labels`` and ``values`` are always the same length.
    """
    model_config = {"frozen": True}

    labels: list[str]          = Field(default_factory=list)
    values: list[NonNegativeInt] = Field(default_factory=list)

    @model_validator(mode="after")
    def _lengths_match(self) -> "SingleSeriesChart":
        if len(self.labels) != len(self.values):
            raise ValueError(
                f"SingleSeriesChart: labels ({len(self.labels)}) and "
                f"values ({len(self.values)}) must have equal length."
            )
        return self

    @classmethod
    def from_points(cls, points: list[tuple[str, int]]) -> "SingleSeriesChart":
        """Build from ``[(label, value), ...]`` — keeps label/value in sync."""
        labels, values = zip(*points) if points else ([], [])
        return cls(labels=list(labels), values=list(values))


class DualSeriesChart(BaseModel):
    """
    Serialised data for a two-dataset chart (grouped bar, multi-line).

    All three lists must have equal length.
    """
    model_config = {"frozen": True}

    labels:       list[str]            = Field(default_factory=list)
    primary:      list[NonNegativeInt] = Field(default_factory=list)
    secondary:    list[NonNegativeInt] = Field(default_factory=list)
    primary_label:   str = Field(default="primary")
    secondary_label: str = Field(default="secondary")

    @model_validator(mode="after")
    def _lengths_match(self) -> "DualSeriesChart":
        lens = {len(self.labels), len(self.primary), len(self.secondary)}
        if len(lens) > 1:
            raise ValueError(
                "DualSeriesChart: labels, primary, and secondary must all have equal length. "
                f"Got: labels={len(self.labels)}, primary={len(self.primary)}, "
                f"secondary={len(self.secondary)}."
            )
        return self

    @classmethod
    def from_points(
        cls,
        points: list[tuple[str, int, int]],
        *,
        primary_label: str = "primary",
        secondary_label: str = "secondary",
    ) -> "DualSeriesChart":
        """Build from ``[(label, primary_val, secondary_val), ...]``."""
        if not points:
            return cls(
                primary_label=primary_label,
                secondary_label=secondary_label,
            )
        labels, primary, secondary = zip(*points)
        return cls(
            labels=list(labels),
            primary=list(primary),
            secondary=list(secondary),
            primary_label=primary_label,
            secondary_label=secondary_label,
        )


# ---------------------------------------------------------------------------
# Shared time-series & distribution point models
# ---------------------------------------------------------------------------

class MonthlyCountPoint(BaseModel):
    """Single-metric data point for a calendar month."""
    model_config = {"frozen": True}

    month: str              = Field(
        description="ISO month string, e.g. '2024-03'.",
        pattern=r"^\d{4}-(0[1-9]|1[0-2])$",
    )
    count: NonNegativeInt


class CombinedMonthlyTrendPoint(BaseModel):
    """Dual-metric data point tracking users and applications per month."""
    model_config = {"frozen": True}

    month:        str             = Field(
        description="ISO month string, e.g. '2024-03'.",
        pattern=r"^\d{4}-(0[1-9]|1[0-2])$",
    )
    users:        NonNegativeInt
    applications: NonNegativeInt


class SectorDistributionPoint(BaseModel):
    """Internship or user count broken down by industry sector."""
    model_config = {"frozen": True}

    sector: str = Field(min_length=1, max_length=120)
    count:  NonNegativeInt
    share:  Percentage = Field(
        default=0.0,
        description="Percentage share of this sector within the total.",
    )


class StatusDistributionPoint(BaseModel):
    """Application count broken down by application status."""
    model_config = {"frozen": True}

    status: ApplicationStatus
    count:  NonNegativeInt
    share:  Percentage = Field(
        default=0.0,
        description="Percentage share of this status within total applications.",
    )


# ---------------------------------------------------------------------------
# Helpers — derived field computation
# ---------------------------------------------------------------------------

def _safe_rate(numerator: int, denominator: int) -> float:
    """Return ``numerator / denominator * 100`` rounded to 2 d.p., or 0.0."""
    if denominator <= 0:
        return 0.0
    return round(min(numerator / denominator * 100, 100.0), 2)


def _with_shares(
    points: list[SectorDistributionPoint],
) -> list[SectorDistributionPoint]:
    """Recompute the ``share`` field on each point so they sum to 100."""
    total = sum(p.count for p in points)
    if total == 0:
        return points
    return [
        p.model_copy(update={"share": round(p.count / total * 100, 2)})
        for p in points
    ]


def _status_with_shares(
    points: list[StatusDistributionPoint],
) -> list[StatusDistributionPoint]:
    total = sum(p.count for p in points)
    if total == 0:
        return points
    return [
        p.model_copy(update={"share": round(p.count / total * 100, 2)})
        for p in points
    ]


# ---------------------------------------------------------------------------
# Summary models
# ---------------------------------------------------------------------------

class DashboardSummary(BaseModel):
    """
    Top-level KPI summary for the admin dashboard hero section.

    ``application_success_rate`` is derived from
    ``successful_applications / total_applications`` and must not be
    supplied independently (it is computed in ``__post_init__``).
    """
    model_config = {"frozen": True}

    total_users:              NonNegativeInt
    active_users:             NonNegativeInt
    total_internships:        NonNegativeInt
    active_internships:       NonNegativeInt
    completed_internships:    NonNegativeInt
    total_applications:       NonNegativeInt
    successful_applications:  NonNegativeInt = Field(default=0)
    certificates_issued:      NonNegativeInt = Field(default=0)

    # Derived — computed by validator, not supplied by caller
    application_success_rate: Percentage     = Field(default=0.0)
    active_user_rate:         Percentage     = Field(default=0.0)
    active_internship_rate:   Percentage     = Field(default=0.0)

    @model_validator(mode="after")
    def _compute_rates(self) -> "DashboardSummary":
        object.__setattr__(
            self,
            "application_success_rate",
            _safe_rate(self.successful_applications, self.total_applications),
        )
        object.__setattr__(
            self,
            "active_user_rate",
            _safe_rate(self.active_users, self.total_users),
        )
        object.__setattr__(
            self,
            "active_internship_rate",
            _safe_rate(self.active_internships, self.total_internships),
        )

        if self.active_users > self.total_users:
            raise ValueError(
                f"active_users ({self.active_users}) cannot exceed "
                f"total_users ({self.total_users})."
            )
        if self.active_internships > self.total_internships:
            raise ValueError(
                f"active_internships ({self.active_internships}) cannot exceed "
                f"total_internships ({self.total_internships})."
            )
        if self.successful_applications > self.total_applications:
            raise ValueError(
                f"successful_applications ({self.successful_applications}) cannot exceed "
                f"total_applications ({self.total_applications})."
            )
        return self


# ---------------------------------------------------------------------------
# Chart container
# ---------------------------------------------------------------------------

class DashboardCharts(BaseModel):
    """
    Pre-serialised chart payloads ready for direct consumption by the frontend.

    Generated from structured point lists via ``DashboardCharts.from_analytics``.
    """
    model_config = {"frozen": True}

    sector_distribution: SingleSeriesChart
    monthly_trends:      DualSeriesChart

    @classmethod
    def from_analytics(
        cls,
        *,
        sector_points: list[SectorDistributionPoint],
        trend_points:  list[CombinedMonthlyTrendPoint],
    ) -> "DashboardCharts":
        """
        Build chart models from structured point lists.

        This is the only sanctioned way to construct ``DashboardCharts`` —
        it ensures labels and values can never fall out of sync.
        """
        sector_chart = SingleSeriesChart.from_points(
            [(p.sector, p.count) for p in sector_points]
        )
        trend_chart = DualSeriesChart.from_points(
            [(p.month, p.users, p.applications) for p in trend_points],
            primary_label="users",
            secondary_label="applications",
        )
        return cls(sector_distribution=sector_chart, monthly_trends=trend_chart)


# ---------------------------------------------------------------------------
# Full API response models
# ---------------------------------------------------------------------------

class DashboardAnalyticsResponse(BaseModel):
    """
    Complete payload for the ``GET /admin/analytics/dashboard`` endpoint.

    ``charts`` is always consistent with ``sector_distribution`` and
    ``monthly_trends`` — both are derived from the same point lists.
    ``sector_distribution`` shares are auto-computed.
    """
    model_config = {"frozen": True}

    summary:             DashboardSummary
    sector_distribution: list[SectorDistributionPoint] = Field(default_factory=list)
    monthly_trends:      list[CombinedMonthlyTrendPoint] = Field(default_factory=list)
    charts:              DashboardCharts

    @model_validator(mode="after")
    def _normalise_shares(self) -> "DashboardAnalyticsResponse":
        object.__setattr__(
            self,
            "sector_distribution",
            _with_shares(list(self.sector_distribution)),
        )
        return self

    @classmethod
    def build(
        cls,
        *,
        summary:             DashboardSummary,
        sector_distribution: list[SectorDistributionPoint],
        monthly_trends:      list[CombinedMonthlyTrendPoint],
    ) -> "DashboardAnalyticsResponse":
        """
        Preferred constructor: builds ``charts`` automatically from point lists.

        Callers should never construct ``DashboardCharts`` manually.
        """
        return cls(
            summary=summary,
            sector_distribution=sector_distribution,
            monthly_trends=monthly_trends,
            charts=DashboardCharts.from_analytics(
                sector_points=sector_distribution,
                trend_points=monthly_trends,
            ),
        )


class AdminOverviewResponse(BaseModel):
    """
    Payload for the ``GET /admin/overview`` summary endpoint.

    ``success_rate`` is derived from ``total_applications`` and
    ``successful_applications`` — never supplied directly by the caller.
    """
    model_config = {"frozen": True}

    total_users:            NonNegativeInt
    total_students:         NonNegativeInt
    total_companies:        NonNegativeInt
    total_internships:      NonNegativeInt
    total_applications:     NonNegativeInt
    successful_applications: NonNegativeInt = Field(default=0)

    # Derived
    success_rate:           Percentage     = Field(default=0.0)

    monthly_stats:          list[CombinedMonthlyTrendPoint] = Field(default_factory=list)
    sector_distribution:    list[SectorDistributionPoint]   = Field(default_factory=list)

    @model_validator(mode="after")
    def _compute_and_validate(self) -> "AdminOverviewResponse":
        object.__setattr__(
            self,
            "success_rate",
            _safe_rate(self.successful_applications, self.total_applications),
        )
        if self.total_students + self.total_companies > self.total_users:
            raise ValueError(
                "total_students + total_companies cannot exceed total_users. "
                f"Got: {self.total_students} + {self.total_companies} > {self.total_users}."
            )
        object.__setattr__(
            self,
            "sector_distribution",
            _with_shares(list(self.sector_distribution)),
        )
        return self


class UsersAnalyticsResponse(BaseModel):
    """
    Payload for the ``GET /admin/analytics/users`` endpoint.

    ``active_user_rate`` is derived; ``chart`` is built from ``monthly_trends``.
    """
    model_config = {"frozen": True}

    total_users:      NonNegativeInt
    active_users:     NonNegativeInt
    active_user_rate: Percentage     = Field(default=0.0)
    monthly_trends:   list[MonthlyCountPoint] = Field(default_factory=list)
    chart:            SingleSeriesChart       = Field(
        default_factory=SingleSeriesChart,
        description="Pre-serialised chart derived from monthly_trends.",
    )

    @model_validator(mode="after")
    def _compute(self) -> "UsersAnalyticsResponse":
        if self.active_users > self.total_users:
            raise ValueError(
                f"active_users ({self.active_users}) cannot exceed "
                f"total_users ({self.total_users})."
            )
        object.__setattr__(
            self,
            "active_user_rate",
            _safe_rate(self.active_users, self.total_users),
        )
        object.__setattr__(
            self,
            "chart",
            SingleSeriesChart.from_points(
                [(p.month, p.count) for p in self.monthly_trends]
            ),
        )
        return self


class InternshipsAnalyticsResponse(BaseModel):
    """
    Payload for the ``GET /admin/analytics/internships`` endpoint.

    ``completion_rate`` is derived; ``chart`` is built from ``sector_distribution``.
    """
    model_config = {"frozen": True}

    total_internships:     NonNegativeInt
    active_internships:    NonNegativeInt
    completed_internships: NonNegativeInt
    sector_distribution:   list[SectorDistributionPoint] = Field(default_factory=list)
    chart:                 SingleSeriesChart              = Field(
        default_factory=SingleSeriesChart,
        description="Pre-serialised sector chart.",
    )

    # Derived
    active_rate:     Percentage = Field(default=0.0)
    completion_rate: Percentage = Field(default=0.0)

    @model_validator(mode="after")
    def _compute(self) -> "InternshipsAnalyticsResponse":
        accounted = self.active_internships + self.completed_internships
        if accounted > self.total_internships:
            raise ValueError(
                f"active_internships ({self.active_internships}) + "
                f"completed_internships ({self.completed_internships}) "
                f"cannot exceed total_internships ({self.total_internships}). "
                f"Got sum={accounted}."
            )
        object.__setattr__(
            self, "active_rate",
            _safe_rate(self.active_internships, self.total_internships),
        )
        object.__setattr__(
            self, "completion_rate",
            _safe_rate(self.completed_internships, self.total_internships),
        )
        sectors_with_shares = _with_shares(list(self.sector_distribution))
        object.__setattr__(self, "sector_distribution", sectors_with_shares)
        object.__setattr__(
            self, "chart",
            SingleSeriesChart.from_points(
                [(p.sector, p.count) for p in sectors_with_shares]
            ),
        )
        return self


class ApplicationsAnalyticsResponse(BaseModel):
    """
    Payload for the ``GET /admin/analytics/applications`` endpoint.

    Both chart payloads are derived from their respective point lists.
    ``application_success_rate`` is derived from counts.
    """
    model_config = {"frozen": True}

    total_applications:      NonNegativeInt
    successful_applications: NonNegativeInt = Field(default=0)
    application_success_rate: Percentage   = Field(default=0.0)
    status_distribution:     list[StatusDistributionPoint]  = Field(default_factory=list)
    monthly_trends:          list[MonthlyCountPoint]        = Field(default_factory=list)

    # Pre-serialised charts — derived from point lists
    status_chart:  SingleSeriesChart = Field(default_factory=SingleSeriesChart)
    monthly_chart: SingleSeriesChart = Field(default_factory=SingleSeriesChart)

    @model_validator(mode="after")
    def _compute(self) -> "ApplicationsAnalyticsResponse":
        if self.successful_applications > self.total_applications:
            raise ValueError(
                f"successful_applications ({self.successful_applications}) cannot exceed "
                f"total_applications ({self.total_applications})."
            )
        object.__setattr__(
            self, "application_success_rate",
            _safe_rate(self.successful_applications, self.total_applications),
        )
        status_with_shares = _status_with_shares(list(self.status_distribution))
        object.__setattr__(self, "status_distribution", status_with_shares)
        object.__setattr__(
            self, "status_chart",
            SingleSeriesChart.from_points(
                [(p.status, p.count) for p in status_with_shares]
            ),
        )
        object.__setattr__(
            self, "monthly_chart",
            SingleSeriesChart.from_points(
                [(p.month, p.count) for p in self.monthly_trends]
            ),
        )
        return self