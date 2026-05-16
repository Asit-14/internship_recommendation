"""
Internship–candidate matching engine.

Scoring dimensions
------------------
1. Skill match      – cosine similarity + coverage recall on normalised skill sets
2. Location match   – exact / containment / token-level Jaccard + remote awareness
3. Education match  – ordinal rank gap with partial credit curve
4. Preference match – configurable soft-filter checks with weighted sub-scores

All public functions are pure (no side-effects, no I/O) and fully typed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any

from ai.similarity import cosine_similarity, keyword_overlap_ratio, text_similarity
from ai.skill_extractor import normalize_skill_list


# ---------------------------------------------------------------------------
# Education ontology
# ---------------------------------------------------------------------------

EDUCATION_LEVEL_RANK: dict[str, int] = {
    "high_school": 1,
    "diploma":     2,
    "bachelor":    3,
    "master":      4,
    "phd":         5,
}

# Partial credit when the candidate is below the required level
# key = rank_gap (required_rank - user_rank), value = score [0, 100]
_EDUCATION_GAP_SCORE: dict[int, float] = {
    0: 100.0,
    1:  65.0,   # one level below → strong partial credit
    2:  35.0,   # two levels below → weak partial credit
    3:  10.0,   # three levels below → near miss
}
# anything beyond gap 3 → 0.0

EDUCATION_KEYWORDS: dict[str, tuple[str, ...]] = {
    "high_school": (
        "high school", "higher secondary", "12th", "hsc", "ssc", "matric",
    ),
    "diploma": (
        "diploma", "associate degree", "associate's", "polytechnic",
    ),
    "bachelor": (
        "bachelor", "b.tech", "b.e", "b.sc", "b.com", "b.a",
        "be ", "btech", "bs ", "bsc", "undergraduate", "graduation",
        "b.eng", "honours",
    ),
    "master": (
        "master", "m.tech", "m.e", "m.sc", "mba", "m.b.a",
        "ms ", "msc", "mtech", "postgraduate", "pg diploma",
        "m.eng",
    ),
    "phd": (
        "phd", "ph.d", "doctorate", "doctoral", "d.phil",
    ),
}

# Remote / hybrid location indicators
_REMOTE_TOKENS: frozenset[str] = frozenset(
    {"remote", "wfh", "work from home", "hybrid", "anywhere", "virtual"}
)

_WHITESPACE_RE = re.compile(r"\s+")


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ScoreWeights:
    """
    Fractional weights for each scoring dimension.

    Must sum to exactly 1.0; validated in ``__post_init__``.

    Defaults reflect that skill alignment is the primary hiring signal,
    while preferences are a soft tie-breaker.
    """
    skill_match:      float = 0.50
    location_match:   float = 0.20
    education_match:  float = 0.20
    preference_match: float = 0.10

    def __post_init__(self) -> None:
        total = (
            self.skill_match
            + self.location_match
            + self.education_match
            + self.preference_match
        )
        if abs(total - 1.0) > 1e-6:
            raise ValueError(
                f"ScoreWeights must sum to 1.0, got {total:.6f}. "
                "Adjust the four fields so they add up to 1."
            )


@dataclass(frozen=True)
class EducationMatchDetails:
    user_level:     str | None
    required_level: str | None
    rank_gap:       int | None = None   # None when requirement is unknown


@dataclass(frozen=True)
class ScoreBreakdown:
    skill_match:      float
    location_match:   float
    education_match:  float
    preference_match: float
    total_score:      float
    education_details: EducationMatchDetails

    def as_dict(self) -> dict[str, Any]:
        """Serialisable snapshot — handy for logging / API responses."""
        return {
            "skill_match":      self.skill_match,
            "location_match":   self.location_match,
            "education_match":  self.education_match,
            "preference_match": self.preference_match,
            "total_score":      self.total_score,
            "education_details": {
                "user_level":     self.education_details.user_level,
                "required_level": self.education_details.required_level,
                "rank_gap":       self.education_details.rank_gap,
            },
        }


# ---------------------------------------------------------------------------
# Education helpers
# ---------------------------------------------------------------------------

@lru_cache(maxsize=2048)
def normalize_education_level(education_text: str | None) -> str | None:
    """
    Map free-form education text to a canonical level key.

    Returns ``None`` when no level can be inferred (e.g. empty input).
    Result is cached so repeated calls with the same string are free.

    >>> normalize_education_level("pursuing B.Tech in CS")
    'bachelor'
    >>> normalize_education_level("PhD Candidate")
    'phd'
    """
    if not education_text:
        return None

    lowered = _WHITESPACE_RE.sub(" ", education_text.strip().lower())

    # Scan from highest to lowest so "phd" beats "bachelor" in hybrid text
    for level in reversed(list(EDUCATION_LEVEL_RANK)):
        if any(kw in lowered for kw in EDUCATION_KEYWORDS[level]):
            return level

    return None


def infer_required_education(*texts: str | None) -> str | None:
    """
    Infer the *highest* education level mentioned across one or more texts.

    Scans the concatenated text and returns the highest matched level,
    since a job posting that mentions both "bachelor" and "master preferred"
    should be treated as requiring a master's.

    >>> infer_required_education("BS required", "Master's preferred")
    'master'
    """
    combined = " ".join(t.strip().lower() for t in texts if t)
    if not combined:
        return None

    matched: list[str] = [
        level
        for level, keywords in EDUCATION_KEYWORDS.items()
        if any(kw in combined for kw in keywords)
    ]

    return max(matched, key=lambda lv: EDUCATION_LEVEL_RANK[lv]) if matched else None


# ---------------------------------------------------------------------------
# Individual score calculators
# ---------------------------------------------------------------------------

def calculate_skill_match_score(
    user_skills: list[str],
    internship_skills: list[str],
) -> float:
    """
    Blended skill score: 60 % cosine similarity + 40 % coverage recall.

    Cosine similarity rewards having a similar *breadth* of relevant skills,
    while the coverage (recall) term penalises missing required skills even
    when the user has many unrelated ones.

    Returns a value in [0, 100] rounded to 2 decimal places.
    """
    norm_user = normalize_skill_list(user_skills)
    norm_internship = normalize_skill_list(internship_skills)

    if not norm_user or not norm_internship:
        return 0.0

    cosine  = cosine_similarity(norm_user, norm_internship)
    coverage = keyword_overlap_ratio(norm_user, norm_internship)

    raw = cosine * 0.6 + coverage * 0.4
    return round(raw * 100, 2)


def _is_remote(location: str) -> bool:
    """Return True when a normalised location string signals remote work."""
    return any(token in location for token in _REMOTE_TOKENS)


def calculate_location_match_score(
    user_location: str | None,
    internship_location: str | None,
) -> float:
    """
    Tiered location match with remote-awareness.

    Score tiers
    -----------
    100 – exact match after normalisation
     95 – one string is a substring of the other (city inside "City, State")
     85 – both sides indicate remote / hybrid work
     70 – internship is remote → any user location qualifies
     0–80 – token-level Jaccard similarity (handles partial city/state overlap)
    """
    if not user_location or not internship_location:
        return 0.0

    norm_user   = _WHITESPACE_RE.sub(" ", user_location.strip().lower())
    norm_intern = _WHITESPACE_RE.sub(" ", internship_location.strip().lower())

    if norm_user == norm_intern:
        return 100.0

    if norm_user in norm_intern or norm_intern in norm_user:
        return 95.0

    user_remote   = _is_remote(norm_user)
    intern_remote = _is_remote(norm_intern)

    if user_remote and intern_remote:
        return 85.0

    if intern_remote:
        # Internship is fully remote → any location can apply
        return 70.0

    jaccard = text_similarity(norm_user, norm_intern)
    return round(jaccard * 80, 2)   # cap token similarity at 80 (not a real match)


def calculate_education_match_score(
    user_education: str | None,
    internship_title: str | None,
    internship_description: str | None,
) -> tuple[float, EducationMatchDetails]:
    """
    Ordinal education match with a smooth partial-credit curve.

    When the internship states no education requirement the candidate always
    scores 100.  When the candidate's level is unknown they score 0.

    The rank-gap table (``_EDUCATION_GAP_SCORE``) assigns partial credit for
    being one, two, or three levels below the requirement, reaching 0 beyond
    gap 3.

    Returns
    -------
    (score, EducationMatchDetails)
    """
    user_level     = normalize_education_level(user_education)
    required_level = infer_required_education(internship_title, internship_description)

    if required_level is None:
        # No stated requirement → full marks
        return 100.0, EducationMatchDetails(
            user_level=user_level,
            required_level=None,
            rank_gap=None,
        )

    if user_level is None:
        # Requirement exists but we cannot determine user's level → zero
        return 0.0, EducationMatchDetails(
            user_level=None,
            required_level=required_level,
            rank_gap=None,
        )

    user_rank     = EDUCATION_LEVEL_RANK[user_level]
    required_rank = EDUCATION_LEVEL_RANK[required_level]
    gap           = max(0, required_rank - user_rank)

    score = _EDUCATION_GAP_SCORE.get(gap, 0.0)

    return score, EducationMatchDetails(
        user_level=user_level,
        required_level=required_level,
        rank_gap=gap,
    )


def _normalize_text_set(values: list[str] | None) -> frozenset[str]:
    """Strip + lowercase + deduplicate a list of strings into a frozenset."""
    if not values:
        return frozenset()
    return frozenset(v.strip().lower() for v in values if v.strip())


def _stipend_score(internship_stipend: int, minimum_stipend: int) -> float:
    """
    Graduated stipend score instead of a binary pass/fail.

    - At or above minimum        → 100
    - Within 20 % below minimum  → linear partial credit [50, 100)
    - More than 20 % below       → 0
    """
    if internship_stipend >= minimum_stipend:
        return 100.0
    if minimum_stipend == 0:
        return 100.0
    ratio = internship_stipend / minimum_stipend
    if ratio >= 0.80:
        return round((ratio - 0.80) / 0.20 * 50 + 50, 2)
    return 0.0


def _duration_score(internship_duration: int, maximum_duration: int) -> float:
    """
    Graduated duration score instead of a binary pass/fail.

    - At or below maximum           → 100
    - Within 20 % above maximum     → linear partial credit [50, 100)
    - More than 20 % above maximum  → 0
    """
    if internship_duration <= maximum_duration:
        return 100.0
    if maximum_duration == 0:
        return 0.0
    ratio = maximum_duration / internship_duration
    if ratio >= 0.80:
        return round((ratio - 0.80) / 0.20 * 50 + 50, 2)
    return 0.0


def calculate_preference_match_score(
    preferences: dict[str, Any] | None,
    *,
    internship_sector:   str,
    internship_company:  str,
    internship_stipend:  int,
    internship_duration: int,
    internship_location: str,
) -> float:
    """
    Weighted preference score across up to five soft-filter dimensions.

    Each active preference contributes its own weight so that a candidate
    with only one preference set is not penalised for missing the others.

    Dimension weights
    -----------------
    sector    0.25   – industry fit
    company   0.15   – named employer preference
    stipend   0.30   – compensation floor (graduated, not binary)
    duration  0.20   – maximum commitment length (graduated)
    remote    0.10   – remote-only flag

    Returns a value in [0, 100] rounded to 2 decimal places.
    """
    if not preferences:
        return 100.0

    # Sub-score weights (must sum to 1.0 across active checks)
    _WEIGHTS = {
        "sector":   0.25,
        "company":  0.15,
        "stipend":  0.30,
        "duration": 0.20,
        "remote":   0.10,
    }

    weighted_sum  = 0.0
    active_weight = 0.0

    # ── Sector ───────────────────────────────────────────────────────────────
    preferred_sectors = _normalize_text_set(preferences.get("preferred_sectors"))
    if preferred_sectors:
        norm_sector = internship_sector.strip().lower()
        # Partial match: sector string contains any preferred keyword
        sector_hit = norm_sector in preferred_sectors or any(
            ps in norm_sector for ps in preferred_sectors
        )
        weighted_sum  += _WEIGHTS["sector"] * (100.0 if sector_hit else 0.0)
        active_weight += _WEIGHTS["sector"]

    # ── Company ──────────────────────────────────────────────────────────────
    preferred_companies = _normalize_text_set(preferences.get("preferred_companies"))
    if preferred_companies:
        norm_company = internship_company.strip().lower()
        company_hit = any(
            pc in norm_company or norm_company in pc
            for pc in preferred_companies
        )
        weighted_sum  += _WEIGHTS["company"] * (100.0 if company_hit else 0.0)
        active_weight += _WEIGHTS["company"]

    # ── Stipend ──────────────────────────────────────────────────────────────
    minimum_stipend = preferences.get("minimum_stipend")
    if minimum_stipend is not None:
        weighted_sum  += _WEIGHTS["stipend"] * _stipend_score(
            internship_stipend, int(minimum_stipend)
        )
        active_weight += _WEIGHTS["stipend"]

    # ── Duration ─────────────────────────────────────────────────────────────
    maximum_duration = preferences.get("maximum_duration_weeks")
    if maximum_duration is not None:
        weighted_sum  += _WEIGHTS["duration"] * _duration_score(
            internship_duration, int(maximum_duration)
        )
        active_weight += _WEIGHTS["duration"]

    # ── Remote ───────────────────────────────────────────────────────────────
    if preferences.get("remote_only"):
        norm_loc   = internship_location.strip().lower()
        remote_hit = _is_remote(norm_loc)
        weighted_sum  += _WEIGHTS["remote"] * (100.0 if remote_hit else 0.0)
        active_weight += _WEIGHTS["remote"]

    if active_weight == 0.0:
        return 100.0

    # Re-normalise by the weight of active checks only
    return round(weighted_sum / active_weight, 2)


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def calculate_weighted_score(
    *,
    user_skills:          list[str],
    user_location:        str | None,
    user_education:       str | None,
    internship_skills:    list[str],
    internship_location:  str,
    internship_title:     str | None,
    internship_description: str | None,
    internship_sector:    str,
    internship_company:   str,
    internship_stipend:   int,
    internship_duration:  int,
    preferences:          dict[str, Any] | None,
    weights:              ScoreWeights | None = None,
) -> ScoreBreakdown:
    """
    Compute the overall weighted match score between a candidate and an internship.

    All individual scores are in [0, 100].  The total score is their weighted
    average, also in [0, 100].

    Returns a single ``ScoreBreakdown`` dataclass that embeds
    ``EducationMatchDetails``, eliminating the old awkward two-tuple return.

    Args:
        user_skills:             Candidate's extracted/declared skills.
        user_location:           Candidate's preferred or current location.
        user_education:          Free-form education string from the candidate's profile.
        internship_skills:       Skills listed in the internship posting.
        internship_location:     Location of the internship.
        internship_title:        Job title (used for education inference).
        internship_description:  Full description text (used for education inference).
        internship_sector:       Industry sector (e.g. "FinTech", "Healthcare").
        internship_company:      Employer name.
        internship_stipend:      Monthly stipend in INR (or any consistent unit).
        internship_duration:     Duration in weeks.
        preferences:             Candidate's soft preferences dict.
        weights:                 Custom ``ScoreWeights``; defaults to the preset.

    Returns:
        ``ScoreBreakdown`` with per-dimension scores, total, and education details.
    """
    active_weights = weights or ScoreWeights()

    skill_score = calculate_skill_match_score(user_skills, internship_skills)

    location_score = calculate_location_match_score(user_location, internship_location)

    education_score, education_details = calculate_education_match_score(
        user_education, internship_title, internship_description,
    )

    preference_score = calculate_preference_match_score(
        preferences,
        internship_sector=internship_sector,
        internship_company=internship_company,
        internship_stipend=internship_stipend,
        internship_duration=internship_duration,
        internship_location=internship_location,
    )

    total = round(
        skill_score      * active_weights.skill_match
        + location_score * active_weights.location_match
        + education_score * active_weights.education_match
        + preference_score * active_weights.preference_match,
        2,
    )

    return ScoreBreakdown(
        skill_match=skill_score,
        location_match=location_score,
        education_match=education_score,
        preference_match=preference_score,
        total_score=total,
        education_details=education_details,
    )