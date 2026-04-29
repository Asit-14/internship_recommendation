import math
import re
from collections.abc import Iterable


TOKEN_PATTERN = re.compile(r"[a-z0-9\+\#\.]+")


def _normalize_values(values: Iterable[str] | None) -> set[str]:
    if not values:
        return set()

    normalized: set[str] = set()
    for value in values:
        cleaned = value.strip().lower()
        if cleaned:
            normalized.add(cleaned)

    return normalized


def cosine_similarity(left_values: Iterable[str] | None, right_values: Iterable[str] | None) -> float:
    """Return cosine similarity on binary vectors built from keyword sets."""
    left = _normalize_values(left_values)
    right = _normalize_values(right_values)

    if not left or not right:
        return 0.0

    dot_product = float(len(left.intersection(right)))
    denominator = math.sqrt(len(left)) * math.sqrt(len(right))

    if denominator == 0:
        return 0.0

    return dot_product / denominator


def keyword_overlap_ratio(candidate_values: Iterable[str] | None, target_values: Iterable[str] | None) -> float:
    """Return coverage of target keywords by candidate keywords."""
    candidate_set = _normalize_values(candidate_values)
    target_set = _normalize_values(target_values)

    if not candidate_set or not target_set:
        return 0.0

    overlap = candidate_set.intersection(target_set)
    return len(overlap) / len(target_set)


def text_similarity(left_text: str | None, right_text: str | None) -> float:
    """Compute Jaccard similarity between tokenized texts."""
    if not left_text or not right_text:
        return 0.0

    left_tokens = set(TOKEN_PATTERN.findall(left_text.strip().lower()))
    right_tokens = set(TOKEN_PATTERN.findall(right_text.strip().lower()))

    if not left_tokens or not right_tokens:
        return 0.0

    intersection = left_tokens.intersection(right_tokens)
    union = left_tokens.union(right_tokens)

    if not union:
        return 0.0

    return len(intersection) / len(union)
