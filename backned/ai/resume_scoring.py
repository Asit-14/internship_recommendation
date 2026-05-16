"""
Resume–internship experience matching engine.

Responsibilities
----------------
- Map free-form experience text to a structured ``ExperienceProfile``.
- Score the gap between a candidate's experience and a posting's requirement
  using a smooth partial-credit curve that combines *years* and *level* signals.
- Assemble the final ``ResumeScoreBreakdown`` with configurable weights.

Design principles
-----------------
- Pure functions only — no I/O, no global mutation.
- Immutable dataclasses throughout.
- Smooth scoring curves instead of hard binary thresholds.
- Every public symbol is fully typed and docstring-documented.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from ai.resume_parser import ExperienceProfile, extract_experience_profile


# ---------------------------------------------------------------------------
# Ordinal experience ontology
# ---------------------------------------------------------------------------

EXPERIENCE_LEVEL_RANK: dict[str, int] = {
    "intern":   0,   # no professional experience expected
    "entry":    1,   # 0–1 years
    "junior":   2,   # 1–3 years
    "mid":      3,   # 3–6 years
    "senior":   4,   # 6–10 years
    "lead":     5,   # 8–12 years + leadership
    "principal":6,   # 12+ years + architecture ownership
}

# Partial credit by rank gap (required_rank - user_rank).
# Values chosen so the score decays smoothly without hard cliffs.
_LEVEL_GAP_SCORE: dict[int, float] = {
    0: 100.0,
    1:  70.0,   # one level short → still a strong candidate
    2:  40.0,   # two levels short → possible stretch hire
    3:  15.0,   # three levels short → significant gap
}
# gap ≥ 4 → 0.0

# Weight blend for the combined score when BOTH years and level are available.
_YEARS_WEIGHT  = 0.65
_LEVEL_WEIGHT  = 0.35

# Partial credit for years gap (applied as a fraction of full score)
# gap ≤ threshold → score; else next tier.
_YEARS_GAP_THRESHOLDS: list[tuple[float, float]] = [
    (0.5,  90.0),   # ≤ 6 months short → near-perfect
    (1.0,  70.0),   # ≤ 1 year short
    (2.0,  45.0),   # ≤ 2 years short
    (3.0,  20.0),   # ≤ 3 years short
]
# gap > 3 years → 0.0


# ---------------------------------------------------------------------------
# Score-breakdown dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ExperienceMatchDetails:
    """
    Diagnostic snapshot of the experience comparison.

    Embedded inside ``ResumeScoreBreakdown`` so callers get full
    explainability without a separate return value.
    """
    user_years:      float | None
    required_years:  float | None
    user_level:      str | None
    required_level:  str | None
    years_score:     float | None   # None when years signal was unavailable
    level_score:     float | None   # None when level signal was unavailable
    blend_mode:      str            # "years_only" | "level_only" | "blended" | "default"


@dataclass(frozen=True)
class ResumeScoreWeights:
    """
    Fractional weights for resume-match scoring dimensions.

    Must sum to exactly 1.0; validated in ``__post_init__``.
    """
    skill_match:      float = 0.50
    education_match:  float = 0.20
    location_match:   float = 0.20
    experience_match: float = 0.10

    def __post_init__(self) -> None:
        total = (
            self.skill_match
            + self.education_match
            + self.location_match
            + self.experience_match
        )
        if abs(total - 1.0) > 1e-6:
            raise ValueError(
                f"ResumeScoreWeights must sum to 1.0, got {total:.8f}. "
                "Adjust the four fields so they total exactly 1."
            )


@dataclass(frozen=True)
class ResumeScoreBreakdown:
    """
    Complete scoring result for one candidate–internship pair.

    All individual scores are in [0, 100].  ``total_score`` is their
    weighted average, also in [0, 100].
    """
    skill_match:       float
    location_match:    float
    education_match:   float
    experience_match:  float
    total_score:       float
    experience_details: ExperienceMatchDetails

    def as_dict(self) -> dict[str, Any]:
        """
        Serialisable snapshot for logging, API responses, and debugging.

        Returns a plain ``dict`` with no nested dataclasses.
        """
        return {
            "skill_match":      self.skill_match,
            "location_match":   self.location_match,
            "education_match":  self.education_match,
            "experience_match": self.experience_match,
            "total_score":      self.total_score,
            "experience_details": {
                "user_years":     self.experience_details.user_years,
                "required_years": self.experience_details.required_years,
                "user_level":     self.experience_details.user_level,
                "required_level": self.experience_details.required_level,
                "years_score":    self.experience_details.years_score,
                "level_score":    self.experience_details.level_score,
                "blend_mode":     self.experience_details.blend_mode,
            },
        }


# ---------------------------------------------------------------------------
# Atomic scoring helpers
# ---------------------------------------------------------------------------

def _years_gap_score(user_years: float, required_years: float) -> float:
    """
    Translate a raw years-gap into a [0, 100] score.

    Uses a piecewise-linear decay table (``_YEARS_GAP_THRESHOLDS``) rather
    than hard binary thresholds, so 2.9 years vs 3.0 required doesn't cliff
    to the same score as 0.5 years vs 3.0 required.

    >>> _years_gap_score(3.0, 3.0)
    100.0
    >>> _years_gap_score(2.5, 3.0)   # gap = 0.5 → tier 1
    90.0
    >>> _years_gap_score(0.0, 3.0)   # gap = 3.0 → tier 4
    20.0
    """
    if user_years >= required_years:
        return 100.0

    gap = required_years - user_years
    for threshold, score in _YEARS_GAP_THRESHOLDS:
        if gap <= threshold:
            return score

    return 0.0


def _level_gap_score(user_level: str, required_level: str) -> float:
    """
    Translate an ordinal level gap into a [0, 100] score.

    Uses ``_LEVEL_GAP_SCORE``; unknown levels map to rank 0 (intern).

    >>> _level_gap_score("junior", "junior")
    100.0
    >>> _level_gap_score("entry", "mid")   # gap = 2
    40.0
    """
    user_rank     = EXPERIENCE_LEVEL_RANK.get(user_level, 0)
    required_rank = EXPERIENCE_LEVEL_RANK.get(required_level, 0)

    if user_rank >= required_rank:
        return 100.0

    gap = required_rank - user_rank
    return _LEVEL_GAP_SCORE.get(gap, 0.0)


# ---------------------------------------------------------------------------
# Main experience scorer
# ---------------------------------------------------------------------------

def calculate_experience_match_score(
    user_profile:     ExperienceProfile,
    required_profile: ExperienceProfile,
) -> tuple[float, ExperienceMatchDetails]:
    """
    Score how well a candidate's experience profile meets a posting's requirement.

    Blend strategy
    --------------
    - **No requirement stated** → 100 (no penalty for any candidate).
    - **No user data**          → 0 (cannot assess).
    - **Years only**            → ``_years_gap_score`` alone.
    - **Level only**            → ``_level_gap_score`` alone.
    - **Both available**        → weighted blend (65 % years, 35 % level),
      because concrete years are a more objective signal than self-reported
      or inferred seniority labels.

    Returns
    -------
    ``(score, ExperienceMatchDetails)`` — the score is in [0, 100],
    rounded to 2 decimal places.
    """
    has_required_years  = required_profile.years is not None
    has_required_level  = required_profile.level is not None
    has_user_years      = user_profile.years is not None
    has_user_level      = user_profile.level is not None

    # ── Case 1: no requirement at all ────────────────────────────────────────
    if not has_required_years and not has_required_level:
        details = ExperienceMatchDetails(
            user_years=user_profile.years,
            required_years=None,
            user_level=user_profile.level,
            required_level=None,
            years_score=None,
            level_score=None,
            blend_mode="default",
        )
        return 100.0, details

    # ── Case 2: no user data at all ──────────────────────────────────────────
    if not has_user_years and not has_user_level:
        details = ExperienceMatchDetails(
            user_years=None,
            required_years=required_profile.years,
            user_level=None,
            required_level=required_profile.level,
            years_score=None,
            level_score=None,
            blend_mode="default",
        )
        return 0.0, details

    years_score: float | None = None
    level_score: float | None = None

    # ── Compute years sub-score ───────────────────────────────────────────────
    if has_required_years:
        years_score = (
            _years_gap_score(user_profile.years, required_profile.years)  # type: ignore[arg-type]
            if has_user_years
            else 0.0   # requirement stated but user didn't supply years
        )

    # ── Compute level sub-score ───────────────────────────────────────────────
    if has_required_level:
        level_score = (
            _level_gap_score(user_profile.level, required_profile.level)  # type: ignore[arg-type]
            if has_user_level
            else 0.0
        )

    # ── Blend ─────────────────────────────────────────────────────────────────
    if years_score is not None and level_score is not None:
        raw        = years_score * _YEARS_WEIGHT + level_score * _LEVEL_WEIGHT
        blend_mode = "blended"
    elif years_score is not None:
        raw        = years_score
        blend_mode = "years_only"
    else:
        raw        = level_score  # type: ignore[assignment]
        blend_mode = "level_only"

    score = round(raw, 2)

    details = ExperienceMatchDetails(
        user_years=user_profile.years,
        required_years=required_profile.years,
        user_level=user_profile.level,
        required_level=required_profile.level,
        years_score=years_score,
        level_score=level_score,
        blend_mode=blend_mode,
    )

    return score, details


# ---------------------------------------------------------------------------
# Extraction helper
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1024)
def extract_required_experience(combined_text: str) -> ExperienceProfile:
    """
    Parse a *single, pre-joined* string into an ``ExperienceProfile``.

    The caller is responsible for joining multiple text sources before
    calling this function, which makes the result cacheable by ``lru_cache``
    (functions with ``*args`` cannot be cached directly).

    Args:
        combined_text: Whitespace-normalised concatenation of all relevant
                       text fields (title + description + requirements, etc.).

    Returns:
        Parsed ``ExperienceProfile`` with ``years`` and/or ``level`` populated.

    Example::

        profile = extract_required_experience(
            " ".join(filter(None, [title, description]))
        )
    """
    return extract_experience_profile(combined_text)


def build_required_experience_profile(*texts: str | None) -> ExperienceProfile:
    """
    Convenience wrapper: join multiple nullable text fields and parse them.

    This replaces the old ``extract_required_experience(*texts)`` variadic
    signature, which was incompatible with ``lru_cache``.

    Args:
        *texts: Any number of nullable strings (title, description, etc.).

    Returns:
        Parsed ``ExperienceProfile``.

    Example::

        required = build_required_experience_profile(title, description)
    """
    combined = " ".join(t.strip() for t in texts if t)
    return extract_required_experience(combined)


# ---------------------------------------------------------------------------
# Score assembler
# ---------------------------------------------------------------------------

def build_resume_score_breakdown(
    *,
    skill_match:        float,
    location_match:     float,
    education_match:    float,
    experience_match:   float,
    experience_details: ExperienceMatchDetails,
    weights:            ResumeScoreWeights | None = None,
) -> ResumeScoreBreakdown:
    """
    Assemble a ``ResumeScoreBreakdown`` from pre-computed dimension scores.

    Args:
        skill_match:        Skill overlap score in [0, 100].
        location_match:     Location compatibility score in [0, 100].
        education_match:    Education level score in [0, 100].
        experience_match:   Experience match score in [0, 100].
        experience_details: Diagnostic details from ``calculate_experience_match_score``.
        weights:            Custom weight set; defaults to ``ResumeScoreWeights()``.

    Returns:
        Immutable ``ResumeScoreBreakdown`` with total score embedded.

    Raises:
        ValueError: If any individual score is outside [0, 100].
    """
    active_weights = weights or ResumeScoreWeights()

    # Guard against upstream calculation errors that could silently corrupt totals
    for name, value in (
        ("skill_match",      skill_match),
        ("location_match",   location_match),
        ("education_match",  education_match),
        ("experience_match", experience_match),
    ):
        if not (0.0 <= value <= 100.0):
            raise ValueError(
                f"Score '{name}' must be in [0, 100], got {value!r}. "
                "Check the upstream calculator for bugs."
            )

    total = round(
        skill_match      * active_weights.skill_match
        + education_match  * active_weights.education_match
        + location_match   * active_weights.location_match
        + experience_match * active_weights.experience_match,
        2,
    )

    return ResumeScoreBreakdown(
        skill_match=skill_match,
        location_match=location_match,
        education_match=education_match,
        experience_match=experience_match,
        total_score=total,
        experience_details=experience_details,
    )