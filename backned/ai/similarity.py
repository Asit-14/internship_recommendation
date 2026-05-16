"""
Text and keyword similarity utilities.

Provides cosine similarity (binary vectors), keyword overlap ratio, and
Jaccard-based text similarity — all with consistent normalisation and
fast set arithmetic.
"""

from __future__ import annotations

import math
import re
from collections.abc import Iterable
from functools import lru_cache
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Matches words, version strings, and identifiers (e.g. "c++", "node.js", "py3")
_TOKEN_RE = re.compile(r"[a-z0-9]+(?:[+#.][a-z0-9]+)*")

# Reusable empty frozenset to avoid repeated allocations
_EMPTY: frozenset[str] = frozenset()


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _normalize(values: Iterable[str] | None) -> frozenset[str]:
    """
    Strip, lowercase, and deduplicate an iterable of strings.

    Returns a frozenset so callers can cache results without mutation risk.
    """
    if values is None:
        return _EMPTY

    result: set[str] = set()
    for v in values:
        cleaned = v.strip().lower()
        if cleaned:
            result.add(cleaned)

    return frozenset(result) if result else _EMPTY


@lru_cache(maxsize=4096)
def _tokenize(text: str) -> frozenset[str]:
    """
    Tokenise a pre-lowercased, stripped string into a frozenset of tokens.

    Cached so repeated calls with identical text (common in batch scoring)
    pay zero marginal cost after the first call.
    """
    return frozenset(_TOKEN_RE.findall(text)) or _EMPTY


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def cosine_similarity(
    left_values: Iterable[str] | None,
    right_values: Iterable[str] | None,
) -> float:
    """
    Cosine similarity over binary keyword vectors.

    Each keyword is treated as a dimension with a binary (present/absent)
    value.  The result is the fraction of the geometric mean of both set
    sizes that the two sets share.

    Args:
        left_values:  First collection of keywords.
        right_values: Second collection of keywords.

    Returns:
        Float in [0.0, 1.0]; 0.0 when either side is empty.

    Examples:
        >>> cosine_similarity(["python", "django"], ["python", "flask"])
        0.5
        >>> cosine_similarity([], ["python"])
        0.0
    """
    left = _normalize(left_values)
    right = _normalize(right_values)

    if not left or not right:
        return 0.0

    intersection_size = len(left & right)
    if intersection_size == 0:
        return 0.0

    # sqrt(|A|) * sqrt(|B|) == sqrt(|A| * |B|) — one sqrt call instead of two
    denominator = math.sqrt(len(left) * len(right))
    return intersection_size / denominator


def keyword_overlap_ratio(
    candidate_values: Iterable[str] | None,
    target_values: Iterable[str] | None,
) -> float:
    """
    Recall of target keywords covered by candidate keywords.

    Measures what fraction of *target* keywords appear in *candidate*.
    Useful for checking whether a candidate document/profile covers the
    required skills or topics.

    Args:
        candidate_values: Keywords produced by the candidate.
        target_values:    Keywords that must be covered.

    Returns:
        Float in [0.0, 1.0]; 0.0 when either side is empty.

    Examples:
        >>> keyword_overlap_ratio(["a", "b", "c"], ["a", "b"])
        1.0
        >>> keyword_overlap_ratio(["a"], ["a", "b"])
        0.5
    """
    candidate = _normalize(candidate_values)
    target = _normalize(target_values)

    if not candidate or not target:
        return 0.0

    return len(candidate & target) / len(target)


def text_similarity(
    left_text: str | None,
    right_text: str | None,
) -> float:
    """
    Jaccard similarity between two texts, compared at the token level.

    Tokens are lower-case alphanumeric runs, optionally joined by ``+``,
    ``#``, or ``.`` (to keep identifiers like ``c++``, ``node.js`` intact).

    Tokenisation results are cached, so scoring the same text against many
    others only parses it once.

    Args:
        left_text:  First text string.
        right_text: Second text string.

    Returns:
        Float in [0.0, 1.0]; 0.0 when either text is empty or yields no
        tokens.

    Examples:
        >>> text_similarity("Python web developer", "Python backend developer")
        0.5
        >>> text_similarity("", "anything")
        0.0
    """
    if not left_text or not right_text:
        return 0.0

    left_tokens = _tokenize(left_text.strip().lower())
    right_tokens = _tokenize(right_text.strip().lower())

    if not left_tokens or not right_tokens:
        return 0.0

    intersection_size = len(left_tokens & right_tokens)
    # |A ∪ B| = |A| + |B| - |A ∩ B|  — avoids materialising the union set
    union_size = len(left_tokens) + len(right_tokens) - intersection_size

    return intersection_size / union_size