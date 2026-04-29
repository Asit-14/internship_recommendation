def normalize_optional_text(value: str | None) -> str | None:
    """Strip and validate an optional text field.

    Returns None if the input is None, raises ValueError if the stripped
    result is empty, otherwise returns the stripped string.
    """
    if value is None:
        return None

    normalized = value.strip()
    if not normalized:
        raise ValueError("Field must not be empty")
    return normalized


def normalize_skills(skills: list[str] | None) -> list[str] | None:
    """Deduplicate and strip a list of skill strings (case-insensitive).

    Returns None if input is None. Raises ValueError if no non-empty
    skills remain after normalization.
    """
    if skills is None:
        return None

    normalized_skills: list[str] = []
    seen: set[str] = set()

    for skill in skills:
        normalized = skill.strip()
        if not normalized:
            continue

        lowered = normalized.lower()
        if lowered not in seen:
            seen.add(lowered)
            normalized_skills.append(normalized)

    if not normalized_skills:
        raise ValueError("At least one non-empty skill is required")

    return normalized_skills
