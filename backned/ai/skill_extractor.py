import re
from collections.abc import Iterable


DEFAULT_SKILL_LEXICON: set[str] = {
    "python",
    "java",
    "c++",
    "c#",
    "javascript",
    "typescript",
    "go",
    "rust",
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "redis",
    "html",
    "css",
    "react",
    "angular",
    "vue",
    "node.js",
    "express",
    "fastapi",
    "django",
    "flask",
    "spring boot",
    "rest api",
    "graphql",
    "git",
    "docker",
    "kubernetes",
    "linux",
    "aws",
    "azure",
    "gcp",
    "terraform",
    "ci/cd",
    "pytest",
    "unit testing",
    "pandas",
    "numpy",
    "scikit-learn",
    "tensorflow",
    "pytorch",
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "nlp",
    "data analysis",
    "data visualization",
    "power bi",
    "tableau",
    "excel",
    "communication",
    "problem solving",
    "teamwork",
    "leadership",
    "figma",
    "ui/ux",
    "automation",
    "selenium",
    "qa",
}

SKILL_ALIASES: dict[str, str] = {
    "js": "javascript",
    "ts": "typescript",
    "nodejs": "node.js",
    "node js": "node.js",
    "reactjs": "react",
    "ml": "machine learning",
    "ai": "artificial intelligence",
    "postgres": "postgresql",
    "k8s": "kubernetes",
    "restful api": "rest api",
}


def normalize_skill(skill: str) -> str:
    normalized = re.sub(r"\s+", " ", skill.strip().lower())
    return SKILL_ALIASES.get(normalized, normalized)


def normalize_skill_list(skills: Iterable[str] | None) -> list[str]:
    if not skills:
        return []

    normalized_skills: list[str] = []
    seen: set[str] = set()

    for skill in skills:
        normalized = normalize_skill(skill)
        if not normalized:
            continue

        if normalized not in seen:
            seen.add(normalized)
            normalized_skills.append(normalized)

    return normalized_skills


def _compile_skill_pattern(skill: str) -> re.Pattern[str]:
    escaped = re.escape(skill.lower())
    escaped = escaped.replace(r"\ ", r"[\s\-/]+")
    return re.compile(rf"(?<!\w){escaped}(?!\w)")


def extract_skills_from_text(
    text: str | None,
    *,
    skill_lexicon: Iterable[str] | None = None,
) -> list[str]:
    if not text:
        return []

    normalized_text = text.lower()
    lexicon = set(normalize_skill_list(skill_lexicon or DEFAULT_SKILL_LEXICON))
    if not lexicon:
        return []

    matches_with_position: list[tuple[int, str]] = []

    for skill in lexicon:
        pattern = _compile_skill_pattern(skill)
        match = pattern.search(normalized_text)
        if match:
            matches_with_position.append((match.start(), skill))

    matches_with_position.sort(key=lambda item: item[0])
    return [skill for _, skill in matches_with_position]


def merge_user_skills(
    explicit_skills: Iterable[str] | None,
    resume_text: str | None = None,
    *,
    skill_lexicon: Iterable[str] | None = None,
) -> list[str]:
    normalized_explicit = normalize_skill_list(explicit_skills)
    extracted_from_resume = extract_skills_from_text(
        resume_text,
        skill_lexicon=skill_lexicon,
    )

    merged: list[str] = []
    seen: set[str] = set()

    for skill in normalized_explicit + extracted_from_resume:
        if skill not in seen:
            seen.add(skill)
            merged.append(skill)

    return merged
