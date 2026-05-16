"""
Skill matching and human-readable explanation generation.

Responsibilities
----------------
- Identify matched skills and skill gaps between candidate and internship.
- Build rich, context-aware natural-language explanations for both
  preference-based and resume-based recommendation flows.

Design principles
-----------------
- All functions are pure (no I/O, no global mutation).
- Explanations are assembled from typed segment builders, not ad-hoc
  string concatenation, making each dimension independently testable.
- Score thresholds are named constants, not magic numbers.
- Both explanation builders share a single rendering pipeline to avoid
  logic drift between the two flows.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol, runtime_checkable

from ai.resume_parser import ExperienceProfile
from ai.resume_scoring import ResumeScoreBreakdown
from ai.scoring import ScoreBreakdown
from ai.skill_extractor import normalize_skill_list


# ---------------------------------------------------------------------------
# Thresholds (named constants — no magic numbers in logic)
# ---------------------------------------------------------------------------

_LOCATION_EXACT_THRESHOLD:   float = 99.0   # effectively exact match
_LOCATION_HIGH_THRESHOLD:    float = 85.0   # strong overlap
_LOCATION_PARTIAL_THRESHOLD: float = 30.0   # some token similarity
_SKILL_STRONG_THRESHOLD:     float = 60.0   # majority of skills matched
_SCORE_EXCELLENT_THRESHOLD:  float = 80.0
_SCORE_GOOD_THRESHOLD:       float = 55.0
_SCORE_FAIR_THRESHOLD:       float = 30.0

# How many skills to surface in the explanation (top matches / gaps)
_MAX_SKILLS_SHOWN: int = 5


# ---------------------------------------------------------------------------
# Score qualifier helpers
# ---------------------------------------------------------------------------

def _score_label(score: float) -> str:
    """Map a [0, 100] score to a human-readable quality label."""
    if score >= _SCORE_EXCELLENT_THRESHOLD:
        return "excellent"
    if score >= _SCORE_GOOD_THRESHOLD:
        return "good"
    if score >= _SCORE_FAIR_THRESHOLD:
        return "fair"
    return "low"


def _pct(score: float) -> str:
    """Format a score as a clean percentage string: '72.5%'."""
    return f"{score:.1f}%"


# ---------------------------------------------------------------------------
# Skill analysis
# ---------------------------------------------------------------------------

def identify_matched_skills(
    user_skills:        list[str],
    internship_skills:  list[str],
) -> list[str]:
    """
    Return internship skills that appear in the candidate's skill set.

    Both lists are normalised before comparison so alias variants
    (e.g. ``"js"`` vs ``"javascript"``) are correctly unified.

    Preserves the order of ``internship_skills`` so the result reflects
    the posting's priority rather than the candidate's declared order.

    Args:
        user_skills:       Candidate's skills (raw or pre-normalised).
        internship_skills: Skills listed in the internship posting.

    Returns:
        Ordered list of matched canonical skill strings.
    """
    user_set = frozenset(normalize_skill_list(user_skills))
    return [
        skill
        for skill in normalize_skill_list(internship_skills)
        if skill in user_set
    ]


def identify_skill_gaps(
    user_skills:       list[str],
    internship_skills: list[str],
) -> list[str]:
    """
    Return internship skills that the candidate does not possess.

    The complement of ``identify_matched_skills``; ordering mirrors the
    internship posting's skill list.

    Args:
        user_skills:       Candidate's skills (raw or pre-normalised).
        internship_skills: Skills listed in the internship posting.

    Returns:
        Ordered list of missing canonical skill strings.
    """
    user_set = frozenset(normalize_skill_list(user_skills))
    return [
        skill
        for skill in normalize_skill_list(internship_skills)
        if skill not in user_set
    ]


def skill_coverage_ratio(
    user_skills:       list[str],
    internship_skills: list[str],
) -> float:
    """
    Fraction of internship skills covered by the candidate [0.0, 1.0].

    Returns 0.0 when ``internship_skills`` is empty.

    >>> skill_coverage_ratio(["python", "django"], ["python", "django", "docker"])
    0.6666...
    """
    norm_internship = normalize_skill_list(internship_skills)
    if not norm_internship:
        return 0.0
    matched = identify_matched_skills(user_skills, internship_skills)
    return len(matched) / len(norm_internship)


# ---------------------------------------------------------------------------
# Shared segment builders (pure → independently testable)
# ---------------------------------------------------------------------------

def _skill_segment(
    matched_skills: list[str],
    missing_skills: list[str],
    skill_score:    float,
) -> str:
    """Build the skill-alignment sentence."""
    total     = len(matched_skills) + len(missing_skills)
    matched_n = len(matched_skills)

    if not matched_skills:
        return (
            "No direct skill overlap was detected with this internship's requirements."
        )

    top = ", ".join(matched_skills[:_MAX_SKILLS_SHOWN])
    suffix = f" and {matched_n - _MAX_SKILLS_SHOWN} more" if matched_n > _MAX_SKILLS_SHOWN else ""
    coverage = f"{matched_n}/{total}" if total else f"{matched_n}"

    qualifier = _score_label(skill_score)
    return (
        f"Skill alignment is {qualifier} ({_pct(skill_score)}): "
        f"you match {coverage} required skills including {top}{suffix}."
    )


def _location_segment(
    user_location:        str | None,
    internship_location:  str,
    location_score:       float,
) -> str:
    """Build the location-fit sentence."""
    if not user_location:
        return "No location was found in your profile, so location fit could not be assessed."

    intern_loc = internship_location.strip() or "unspecified"
    user_loc   = user_location.strip()

    if location_score >= _LOCATION_EXACT_THRESHOLD:
        return f"Location is an exact match ({user_loc})."

    if location_score >= _LOCATION_HIGH_THRESHOLD:
        return (
            f"Location is highly compatible: your preference ({user_loc}) "
            f"closely matches the internship location ({intern_loc})."
        )

    if location_score >= _LOCATION_PARTIAL_THRESHOLD:
        return (
            f"Location has partial overlap ({user_loc} vs {intern_loc}). "
            "Some commute or relocation may be required."
        )

    # Check for remote
    remote_tokens = {"remote", "hybrid", "wfh", "work from home", "anywhere"}
    intern_lower  = intern_loc.lower()
    if any(tok in intern_lower for tok in remote_tokens):
        return f"This internship is remote/hybrid — your location ({user_loc}) is not a barrier."

    return (
        f"Location alignment is low ({user_loc} vs {intern_loc}). "
        "Consider whether relocation or remote work is feasible."
    )


def _education_segment(
    user_level:     str | None,
    required_level: str | None,
    edu_score:      float,
) -> str:
    """Build the education-fit sentence."""
    def _fmt(level: str | None) -> str:
        return level.replace("_", " ").title() if level else "unspecified"

    if required_level is None:
        return "No formal education requirement was specified for this internship."

    user_fmt     = _fmt(user_level)
    required_fmt = _fmt(required_level)

    if edu_score >= 100.0:
        return (
            f"Education requirement is fully met: "
            f"your {user_fmt} meets or exceeds the required {required_fmt}."
        )

    if edu_score >= 60.0:
        return (
            f"Education is a partial fit: your {user_fmt} is slightly below "
            f"the preferred {required_fmt}, but you may still be considered."
        )

    if edu_score > 0.0:
        return (
            f"Education gap detected: you have a {user_fmt} but this role "
            f"prefers {required_fmt}. Demonstrating strong skills can offset this."
        )

    return (
        f"Significant education gap: role requires {required_fmt} "
        f"but your profile shows {user_fmt}."
    )


def _skill_gap_segment(missing_skills: list[str]) -> str:
    """Build the skill-gap call-to-action sentence."""
    if not missing_skills:
        return "You cover all listed required skills — great fit on paper."

    shown   = missing_skills[:_MAX_SKILLS_SHOWN]
    extra_n = len(missing_skills) - len(shown)
    top_gaps = ", ".join(shown)
    suffix   = f" and {extra_n} others" if extra_n > 0 else ""

    return (
        f"Primary skills to develop for this role: {top_gaps}{suffix}. "
        "Addressing these gaps would significantly strengthen your application."
    )


def _experience_segment(
    user_exp:     ExperienceProfile,
    required_exp: ExperienceProfile,
    exp_score:    float,
) -> str:
    """Build the experience-fit sentence."""
    def _fmt(profile: ExperienceProfile) -> str:
        if profile.years is not None:
            yr = f"{profile.years:.1f}".rstrip("0").rstrip(".")
            label = f"{yr} year{'s' if profile.years != 1 else ''}"
            if profile.level:
                return f"{label} ({profile.level}-level)"
            return label
        if profile.level:
            return f"{profile.level}-level"
        return "unspecified"

    if required_exp.years is None and required_exp.level is None:
        return "No explicit experience requirement was stated for this role."

    user_fmt     = _fmt(user_exp)
    required_fmt = _fmt(required_exp)

    if exp_score >= 100.0:
        return (
            f"Experience requirement fully met: "
            f"your background ({user_fmt}) meets or exceeds the required ({required_fmt})."
        )

    if exp_score >= 65.0:
        return (
            f"Experience is a close fit: your background ({user_fmt}) is slightly below "
            f"the required ({required_fmt}), but you remain a competitive candidate."
        )

    if exp_score >= 30.0:
        return (
            f"Experience gap noted: you have {user_fmt} against a requirement of {required_fmt}. "
            "Highlight transferable projects and skills in your application."
        )

    return (
        f"Significant experience gap: role requires {required_fmt} "
        f"but your profile shows {user_fmt}. Consider applying for junior or entry-level variants."
    )


def _total_score_segment(total_score: float) -> str:
    """Build the closing overall-score sentence."""
    label = _score_label(total_score)
    return (
        f"Overall match: {_pct(total_score)} — {label}. "
        + {
            "excellent": "You are a strong candidate for this role.",
            "good":      "You are a competitive candidate worth applying to.",
            "fair":      "This is a stretch opportunity — focus on your strongest selling points.",
            "low":       "This role may not be the best fit right now, but it could be a future goal.",
        }[label]
    )


# ---------------------------------------------------------------------------
# Public explanation builders
# ---------------------------------------------------------------------------

def build_recommendation_explanation(
    *,
    matched_skills:           list[str],
    missing_skills:           list[str],
    score_breakdown:          ScoreBreakdown,
    user_location:            str | None,
    internship_location:      str,
    user_education_level:     str | None,
    required_education_level: str | None,
) -> str:
    """
    Build a natural-language explanation for a preference-based recommendation.

    Each dimension (skills, location, education, gaps, total) is rendered
    by a dedicated segment builder and joined into a single coherent paragraph.

    Args:
        matched_skills:           Skills present in both profiles.
        missing_skills:           Skills required but absent from candidate.
        score_breakdown:          Full per-dimension score object.
        user_location:            Candidate's location string.
        internship_location:      Internship location string.
        user_education_level:     Candidate's normalised education level.
        required_education_level: Inferred required education level.

    Returns:
        A human-readable paragraph suitable for display in a UI or email.
    """
    segments = [
        _skill_segment(matched_skills, missing_skills, score_breakdown.skill_match),
        _location_segment(user_location, internship_location, score_breakdown.location_match),
        _education_segment(
            user_education_level,
            required_education_level,
            score_breakdown.education_match,
        ),
        _skill_gap_segment(missing_skills),
        _total_score_segment(score_breakdown.total_score),
    ]

    return "  ".join(seg for seg in segments if seg)


def build_resume_recommendation_explanation(
    *,
    matched_skills:           list[str],
    missing_skills:           list[str],
    score_breakdown:          ResumeScoreBreakdown,
    user_location:            str | None,
    internship_location:      str,
    user_education_level:     str | None,
    required_education_level: str | None,
    user_experience:          ExperienceProfile,
    required_experience:      ExperienceProfile,
) -> str:
    """
    Build a natural-language explanation for a resume-based recommendation.

    Extends the preference-based flow with an additional experience-fit
    segment derived from the candidate's parsed resume.

    Args:
        matched_skills:           Skills present in both profiles.
        missing_skills:           Skills required but absent from candidate.
        score_breakdown:          Resume-specific per-dimension score object.
        user_location:            Location extracted from the resume (may be None).
        internship_location:      Internship location string.
        user_education_level:     Education level parsed from the resume.
        required_education_level: Inferred required education level.
        user_experience:          Experience profile parsed from the resume.
        required_experience:      Experience profile inferred from the posting.

    Returns:
        A human-readable paragraph suitable for display in a UI or email.
    """
    segments = [
        _skill_segment(matched_skills, missing_skills, score_breakdown.skill_match),
        _location_segment(user_location, internship_location, score_breakdown.location_match),
        _education_segment(
            user_education_level,
            required_education_level,
            score_breakdown.education_match,
        ),
        _experience_segment(
            user_experience,
            required_experience,
            score_breakdown.experience_match,
        ),
        _skill_gap_segment(missing_skills),
        _total_score_segment(score_breakdown.total_score),
    ]

    return "  ".join(seg for seg in segments if seg)