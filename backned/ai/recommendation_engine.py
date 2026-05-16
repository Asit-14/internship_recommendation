"""
Internship recommendation engine.

Responsibilities
----------------
- Merge and normalise candidate skills from explicit input + resume text.
- Score every candidate–internship pair across four weighted dimensions.
- Rank, filter, and return the top-K results with full explainability.

Design principles
-----------------
- Stateless scoring; the engine holds only immutable configuration.
- Parallel scoring via ``concurrent.futures`` for large internship catalogues.
- Early-exit deduplication to avoid re-scoring the same internship twice.
- Rich result dataclass with serialisation support for API responses.
- Structured logging hooks for production observability.
"""

from __future__ import annotations

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Any, Sequence

from ai.explanation import (
    build_recommendation_explanation,
    identify_matched_skills,
    identify_skill_gaps,
)
from ai.scoring import ScoreBreakdown, ScoreWeights, calculate_weighted_score
from ai.skill_extractor import merge_user_skills
from models.internship_model import Internship
from schemas.recommendation_schema import RecommendationRequest

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Internship catalogue size above which parallel scoring is used
_PARALLEL_THRESHOLD = 20

# Max worker threads for parallel scoring
_MAX_WORKERS = 8

# Internships with total_score below this are excluded from results
DEFAULT_MINIMUM_SCORE: float = 0.0


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RecommendationResult:
    """
    Complete scoring + explainability result for one candidate–internship pair.

    Attributes
    ----------
    internship:      The internship being evaluated.
    score_breakdown: Per-dimension scores and weighted total.
    explanation:     Human-readable explanation of why this internship was recommended.
    matched_skills:  Skills present in both the candidate profile and the posting.
    skill_gap:       Skills required by the posting that the candidate lacks.
    scored_at_ms:    Wall-clock time (ms) taken to score this pair — useful for
                     production latency monitoring.
    """
    internship:     Internship
    score_breakdown: ScoreBreakdown
    explanation:    str
    matched_skills: list[str]
    skill_gap:      list[str]
    scored_at_ms:   float = field(default=0.0)

    def as_dict(self) -> dict[str, Any]:
        """
        Serialisable snapshot for API responses and structured logging.

        Returns a plain ``dict`` with no nested dataclasses.
        """
        return {
            "internship_id":   getattr(self.internship, "id", None),
            "internship_title": getattr(self.internship, "title", None),
            "total_score":     self.score_breakdown.total_score,
            "score_breakdown": {
                "skill_match":      self.score_breakdown.skill_match,
                "location_match":   self.score_breakdown.location_match,
                "education_match":  self.score_breakdown.education_match,
                "preference_match": self.score_breakdown.preference_match,
            },
            "matched_skills":  self.matched_skills,
            "skill_gap":       self.skill_gap,
            "explanation":     self.explanation,
            "scored_at_ms":    self.scored_at_ms,
        }


@dataclass(frozen=True)
class RecommendationBatch:
    """
    Full output of one ``RecommendationEngine.recommend()`` call.

    Attributes
    ----------
    results:               Top-K ranked results.
    normalized_user_skills: Canonical skill list used during scoring
                            (explicit + resume-extracted, deduplicated).
    total_scored:          Total number of internships evaluated.
    skipped:               Internships skipped due to deduplication.
    elapsed_ms:            Total wall-clock time for the entire batch.
    """
    results:                list[RecommendationResult]
    normalized_user_skills: list[str]
    total_scored:           int
    skipped:                int
    elapsed_ms:             float

    def as_dict(self) -> dict[str, Any]:
        return {
            "results":                [r.as_dict() for r in self.results],
            "normalized_user_skills": self.normalized_user_skills,
            "total_scored":           self.total_scored,
            "skipped":                self.skipped,
            "elapsed_ms":             self.elapsed_ms,
        }


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

class RecommendationEngine:
    """
    Stateless internship recommendation engine with configurable scoring weights.

    Usage
    -----
    ::

        engine = RecommendationEngine(
            weights=ScoreWeights(skill_match=0.6, location_match=0.15,
                                 education_match=0.15, preference_match=0.10),
            minimum_score=10.0,
            parallel_threshold=50,
        )
        batch = engine.recommend(
            user_profile=request,
            internships=catalogue,
        )
        top_results = batch.results

    Parameters
    ----------
    weights:            Custom dimension weights; defaults to ``ScoreWeights()``.
    minimum_score:      Internships scoring below this threshold are excluded
                        from the output even if they rank in the top-K.
    parallel_threshold: Minimum catalogue size to trigger parallel scoring.
    max_workers:        Thread-pool size for parallel scoring.
    """

    def __init__(
        self,
        *,
        weights:            ScoreWeights | None = None,
        minimum_score:      float = DEFAULT_MINIMUM_SCORE,
        parallel_threshold: int = _PARALLEL_THRESHOLD,
        max_workers:        int = _MAX_WORKERS,
    ) -> None:
        self.weights            = weights or ScoreWeights()
        self.minimum_score      = minimum_score
        self.parallel_threshold = parallel_threshold
        self.max_workers        = max_workers

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def recommend(
        self,
        *,
        user_profile: RecommendationRequest,
        internships:  Sequence[Internship],
    ) -> RecommendationBatch:
        """
        Score, rank, and return the top-K internships for a candidate.

        Steps
        -----
        1. Merge explicit skills with resume-extracted skills.
        2. Deduplicate the internship catalogue by ID.
        3. Score each internship (parallel when catalogue is large).
        4. Filter by ``minimum_score``.
        5. Sort by (total_score DESC, skill_match DESC).
        6. Return the top ``user_profile.top_k`` results.

        Args:
            user_profile: Candidate profile including skills, location,
                          education, preferences, and ``top_k``.
            internships:  Full catalogue of internships to evaluate.

        Returns:
            ``RecommendationBatch`` with ranked results and diagnostics.
        """
        batch_start = time.perf_counter()

        # ── Step 1: normalise candidate skills ───────────────────────────────
        normalized_user_skills = merge_user_skills(
            explicit_skills=user_profile.skills,
            resume_text=getattr(user_profile, "resume_text", None),
        )

        if not normalized_user_skills:
            logger.warning(
                "No skills could be extracted for candidate. "
                "All skill_match scores will be 0."
            )

        preferences: dict[str, Any] | None = (
            user_profile.preferences.model_dump()
            if user_profile.preferences
            else None
        )

        # ── Step 2: deduplicate catalogue ────────────────────────────────────
        unique_internships, skipped = self._deduplicate(internships)

        if not unique_internships:
            logger.info("Internship catalogue is empty after deduplication.")
            return RecommendationBatch(
                results=[],
                normalized_user_skills=normalized_user_skills,
                total_scored=0,
                skipped=skipped,
                elapsed_ms=0.0,
            )

        # ── Step 3: score ────────────────────────────────────────────────────
        use_parallel = len(unique_internships) >= self.parallel_threshold

        logger.debug(
            "Scoring %d internships for candidate (parallel=%s, skills=%d).",
            len(unique_internships),
            use_parallel,
            len(normalized_user_skills),
        )

        if use_parallel:
            results = self._score_parallel(
                user_profile=user_profile,
                internships=unique_internships,
                normalized_user_skills=normalized_user_skills,
                preferences=preferences,
            )
        else:
            results = self._score_sequential(
                user_profile=user_profile,
                internships=unique_internships,
                normalized_user_skills=normalized_user_skills,
                preferences=preferences,
            )

        # ── Step 4: filter ───────────────────────────────────────────────────
        if self.minimum_score > 0.0:
            before = len(results)
            results = [r for r in results if r.score_breakdown.total_score >= self.minimum_score]
            logger.debug(
                "Filtered %d internships below minimum_score=%.1f.",
                before - len(results),
                self.minimum_score,
            )

        # ── Step 5: rank ─────────────────────────────────────────────────────
        results.sort(
            key=lambda r: (r.score_breakdown.total_score, r.score_breakdown.skill_match),
            reverse=True,
        )

        # ── Step 6: top-K ────────────────────────────────────────────────────
        top_k      = max(1, getattr(user_profile, "top_k", 10))
        top_results = results[:top_k]

        elapsed_ms = (time.perf_counter() - batch_start) * 1000

        logger.info(
            "Recommendation complete: scored=%d skipped=%d returned=%d elapsed=%.1fms",
            len(unique_internships),
            skipped,
            len(top_results),
            elapsed_ms,
        )

        return RecommendationBatch(
            results=top_results,
            normalized_user_skills=normalized_user_skills,
            total_scored=len(unique_internships),
            skipped=skipped,
            elapsed_ms=elapsed_ms,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _deduplicate(
        self,
        internships: Sequence[Internship],
    ) -> tuple[list[Internship], int]:
        """
        Remove duplicate internships by their ``id`` attribute.

        Falls back to object identity when ``id`` is absent.
        First-seen wins; order is preserved.

        Returns ``(unique_list, skipped_count)``.
        """
        seen:   set[Any]       = set()
        unique: list[Internship] = []

        for internship in internships:
            key = getattr(internship, "id", id(internship))
            if key not in seen:
                seen.add(key)
                unique.append(internship)

        return unique, len(internships) - len(unique)

    def _score_one(
        self,
        *,
        internship:             Internship,
        user_profile:           RecommendationRequest,
        normalized_user_skills: list[str],
        preferences:            dict[str, Any] | None,
    ) -> RecommendationResult | None:
        """
        Score a single internship against the candidate profile.

        Returns ``None`` on unexpected errors so parallel scoring can
        continue rather than crashing the entire batch.
        """
        t0 = time.perf_counter()
        try:
            score_breakdown = calculate_weighted_score(
                user_skills=normalized_user_skills,
                user_location=user_profile.location,
                user_education=user_profile.education,
                internship_skills=internship.skills_required,
                internship_location=internship.location,
                internship_title=internship.title,
                internship_description=internship.description,
                internship_sector=internship.sector,
                internship_company=internship.company_name,
                internship_stipend=internship.stipend,
                internship_duration=internship.duration,
                preferences=preferences,
                weights=self.weights,
            )

            matched_skills = identify_matched_skills(
                normalized_user_skills,
                internship.skills_required,
            )
            skill_gap = identify_skill_gaps(
                normalized_user_skills,
                internship.skills_required,
            )

            explanation = build_recommendation_explanation(
                matched_skills=matched_skills,
                missing_skills=skill_gap,
                score_breakdown=score_breakdown,
                user_location=user_profile.location,
                internship_location=internship.location,
                user_education_level=score_breakdown.education_details.user_level,
                required_education_level=score_breakdown.education_details.required_level,
            )

            scored_at_ms = (time.perf_counter() - t0) * 1000

            return RecommendationResult(
                internship=internship,
                score_breakdown=score_breakdown,
                explanation=explanation,
                matched_skills=matched_skills,
                skill_gap=skill_gap,
                scored_at_ms=scored_at_ms,
            )

        except Exception:
            logger.exception(
                "Unexpected error scoring internship '%s' (id=%s). Skipping.",
                getattr(internship, "title", "<unknown>"),
                getattr(internship, "id", "<unknown>"),
            )
            return None

    def _score_sequential(
        self,
        *,
        user_profile:           RecommendationRequest,
        internships:            list[Internship],
        normalized_user_skills: list[str],
        preferences:            dict[str, Any] | None,
    ) -> list[RecommendationResult]:
        """Score internships one at a time (small catalogues)."""
        results: list[RecommendationResult] = []
        for internship in internships:
            result = self._score_one(
                internship=internship,
                user_profile=user_profile,
                normalized_user_skills=normalized_user_skills,
                preferences=preferences,
            )
            if result is not None:
                results.append(result)
        return results

    def _score_parallel(
        self,
        *,
        user_profile:           RecommendationRequest,
        internships:            list[Internship],
        normalized_user_skills: list[str],
        preferences:            dict[str, Any] | None,
    ) -> list[RecommendationResult]:
        """
        Score internships concurrently using a thread pool.

        Thread-safe because ``_score_one`` is a pure function with no
        shared mutable state.  Results are collected as futures complete
        and failures are logged but do not abort the batch.
        """
        results: list[RecommendationResult] = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(
                    self._score_one,
                    internship=internship,
                    user_profile=user_profile,
                    normalized_user_skills=normalized_user_skills,
                    preferences=preferences,
                ): internship
                for internship in internships
            }

            for future in as_completed(futures):
                result = future.result()
                if result is not None:
                    results.append(result)

        return results