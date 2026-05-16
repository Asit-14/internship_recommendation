
from __future__ import annotations

import re
from collections.abc import Iterable
from functools import lru_cache

# ---------------------------------------------------------------------------
# Canonical skill lexicon
# ---------------------------------------------------------------------------

DEFAULT_SKILL_LEXICON: frozenset[str] = frozenset(
    {
        # ── Programming Languages ────────────────────────────────────────────
        "python", "java", "c", "c++", "c#", "go", "rust", "ruby", "php",
        "swift", "kotlin", "scala", "r", "matlab", "perl", "lua", "haskell",
        "elixir", "erlang", "clojure", "f#", "dart", "groovy", "julia",
        "cobol", "fortran", "assembly", "bash", "powershell",
        # ── Web / JavaScript Ecosystem ───────────────────────────────────────
        "javascript", "typescript", "html", "css", "sass", "less",
        "react", "next.js", "remix", "angular", "vue", "nuxt.js",
        "svelte", "sveltekit", "solid.js", "astro", "htmx",
        "node.js", "express", "fastify", "nest.js", "hapi",
        "webpack", "vite", "rollup", "esbuild", "babel",
        "jquery", "tailwind css", "bootstrap", "material ui", "chakra ui",
        "storybook", "cypress", "playwright", "jest", "vitest",
        # ── Backend Frameworks ───────────────────────────────────────────────
        "django", "flask", "fastapi", "starlette", "tornado",
        "spring boot", "spring", "quarkus", "micronaut",
        "rails", "sinatra", "laravel", "symfony", "codeigniter",
        "gin", "echo", "fiber", "actix", "axum", "rocket",
        "phoenix", "ecto", "vapor",
        # ── Databases ────────────────────────────────────────────────────────
        "sql", "mysql", "postgresql", "sqlite", "oracle", "mssql",
        "mongodb", "redis", "elasticsearch", "opensearch", "cassandra",
        "dynamodb", "firestore", "couchdb", "neo4j", "influxdb",
        "clickhouse", "snowflake", "bigquery", "redshift", "supabase",
        "prisma", "sqlalchemy", "hibernate", "sequelize", "typeorm",
        # ── Cloud & Infrastructure ───────────────────────────────────────────
        "aws", "azure", "gcp", "cloudflare", "vercel", "netlify",
        "heroku", "digitalocean", "linode", "hetzner",
        "ec2", "s3", "rds", "lambda", "eks", "ecs", "fargate",
        "azure functions", "azure devops", "google cloud run",
        "terraform", "pulumi", "cdk", "cloudformation", "ansible",
        "puppet", "chef", "packer",
        # ── Containers & Orchestration ───────────────────────────────────────
        "docker", "kubernetes", "helm", "istio", "envoy", "linkerd",
        "docker compose", "podman", "containerd",
        # ── DevOps & CI/CD ───────────────────────────────────────────────────
        "ci/cd", "github actions", "gitlab ci", "jenkins", "circleci",
        "travis ci", "argocd", "flux", "spinnaker", "tekton",
        "git", "github", "gitlab", "bitbucket", "mercurial",
        "linux", "unix", "nginx", "apache", "traefik", "haproxy",
        "prometheus", "grafana", "datadog", "new relic", "splunk",
        "opentelemetry", "jaeger", "zipkin", "elk stack",
        # ── APIs & Messaging ─────────────────────────────────────────────────
        "rest api", "graphql", "grpc", "websocket", "webhook",
        "kafka", "rabbitmq", "celery", "sqs", "pubsub", "nats",
        "openapi", "swagger", "protobuf", "avro",
        # ── Security ─────────────────────────────────────────────────────────
        "oauth", "jwt", "saml", "ldap", "sso", "keycloak",
        "owasp", "penetration testing", "sast", "dast",
        "vault", "secrets management", "zero trust",
        "ssl/tls", "cryptography", "cybersecurity",
        # ── AI / ML / Data Science ───────────────────────────────────────────
        "machine learning", "deep learning", "artificial intelligence",
        "nlp", "computer vision", "reinforcement learning",
        "generative ai", "llm", "rag", "fine-tuning",
        "tensorflow", "pytorch", "keras", "jax",
        "scikit-learn", "xgboost", "lightgbm", "catboost",
        "hugging face", "langchain", "llamaindex", "openai api",
        "pandas", "numpy", "scipy", "matplotlib", "seaborn", "plotly",
        "spark", "hadoop", "dask", "ray",
        "airflow", "prefect", "dagster", "mlflow", "kubeflow",
        "data engineering", "data analysis", "data visualization",
        "feature engineering", "model deployment", "model monitoring",
        "statistics", "a/b testing", "hypothesis testing",
        # ── Business Intelligence ─────────────────────────────────────────────
        "power bi", "tableau", "looker", "metabase", "superset",
        "excel", "google sheets", "dbt",
        # ── Mobile Development ───────────────────────────────────────────────
        "android", "ios", "react native", "flutter", "xamarin",
        "expo", "capacitor", "ionic",
        # ── Testing & QA ─────────────────────────────────────────────────────
        "pytest", "unittest", "junit", "testng", "rspec",
        "selenium", "appium", "postman", "k6", "gatling",
        "unit testing", "integration testing", "e2e testing",
        "tdd", "bdd", "qa",
        # ── Design & Product ─────────────────────────────────────────────────
        "figma", "sketch", "adobe xd", "invision",
        "ui/ux", "product design", "wireframing", "prototyping",
        "user research", "accessibility", "wcag",
        # ── Architecture & Practices ─────────────────────────────────────────
        "microservices", "serverless", "event-driven architecture",
        "domain-driven design", "clean architecture",
        "system design", "distributed systems", "caching",
        "design patterns", "solid principles", "api design",
        "agile", "scrum", "kanban", "jira", "confluence",
        # ── Soft Skills ──────────────────────────────────────────────────────
        "communication", "problem solving", "teamwork", "leadership",
        "mentoring", "code review", "technical writing", "documentation",
        "project management", "stakeholder management",
        "automation",
    }
)

# ---------------------------------------------------------------------------
# Alias table  →  canonical form
# ---------------------------------------------------------------------------

SKILL_ALIASES: dict[str, str] = {
    # JavaScript variants
    "js": "javascript",
    "es6": "javascript",
    "ecmascript": "javascript",
    "ts": "typescript",
    "nodejs": "node.js",
    "node js": "node.js",
    "node": "node.js",
    "reactjs": "react",
    "react.js": "react",
    "nextjs": "next.js",
    "next js": "next.js",
    "nuxtjs": "nuxt.js",
    "nuxt js": "nuxt.js",
    "nestjs": "nest.js",
    "nest js": "nest.js",
    "vuejs": "vue",
    "vue.js": "vue",
    "solidjs": "solid.js",
    "sveltejs": "svelte",
    "tailwind": "tailwind css",
    "tailwindcss": "tailwind css",
    "mui": "material ui",
    # Backend
    "fastapi framework": "fastapi",
    "springboot": "spring boot",
    "spring-boot": "spring boot",
    # Databases
    "postgres": "postgresql",
    "pg": "postgresql",
    "mongo": "mongodb",
    "mssql server": "mssql",
    "sql server": "mssql",
    "elastic": "elasticsearch",
    "es": "elasticsearch",
    "dynamo": "dynamodb",
    "click house": "clickhouse",
    # Cloud
    "amazon web services": "aws",
    "microsoft azure": "azure",
    "google cloud": "gcp",
    "google cloud platform": "gcp",
    "gke": "kubernetes",
    "k8s": "kubernetes",
    # DevOps / CI
    "gh actions": "github actions",
    "github action": "github actions",
    "gitlab-ci": "gitlab ci",
    "cd/ci": "ci/cd",
    "continuous integration": "ci/cd",
    "continuous deployment": "ci/cd",
    # APIs
    "restful api": "rest api",
    "restful": "rest api",
    "rest": "rest api",
    "graphql api": "graphql",
    # AI / ML
    "ml": "machine learning",
    "ai": "artificial intelligence",
    "gen ai": "generative ai",
    "genai": "generative ai",
    "large language model": "llm",
    "natural language processing": "nlp",
    "cv": "computer vision",
    "hf": "hugging face",
    "huggingface": "hugging face",
    "sklearn": "scikit-learn",
    "scikitlearn": "scikit-learn",
    "xgb": "xgboost",
    "lgbm": "lightgbm",
    "openai": "openai api",
    # Testing
    "tdd": "tdd",
    "bdd": "bdd",
    "quality assurance": "qa",
    "end to end testing": "e2e testing",
    "end-to-end testing": "e2e testing",
    # Design
    "ux": "ui/ux",
    "ui": "ui/ux",
    "ux/ui": "ui/ux",
    # Security
    "tls": "ssl/tls",
    "ssl": "ssl/tls",
    "pentest": "penetration testing",
    "pen testing": "penetration testing",
    # Mobile
    "rn": "react native",
    # Misc
    "ddd": "domain-driven design",
    "pb": "power bi",
    "powerbi": "power bi",
}

# ---------------------------------------------------------------------------
# Pre-compilation — done once at import time
# ---------------------------------------------------------------------------

def _build_combined_pattern(lexicon: frozenset[str]) -> re.Pattern[str]:
    """
    Build a single alternation regex that matches any skill in *lexicon*.

    Skills are sorted longest-first so that "spring boot" matches before
    "spring" on engines that use leftmost-first alternation.

    Each skill token is escaped and internal spaces are replaced with a
    flexible ``[\\s\\-/]+`` connector so "ci/cd", "ci cd", and "ci-cd"
    all match.
    """
    # Sort longest first to prefer "spring boot" over "spring"
    sorted_skills = sorted(lexicon, key=len, reverse=True)

    parts: list[str] = []
    for skill in sorted_skills:
        escaped = re.escape(skill)
        # Allow flexible separators between words
        escaped = re.sub(r"(?<=\w)(\\ )+(?=\w)", r"[\\s\\-/]+", escaped)
        parts.append(escaped)

    pattern_str = r"(?<!\w)(?:" + "|".join(parts) + r")(?!\w)"
    return re.compile(pattern_str, re.IGNORECASE)


# Module-level compiled pattern for the default lexicon
_DEFAULT_PATTERN: re.Pattern[str] = _build_combined_pattern(DEFAULT_SKILL_LEXICON)

# Cache custom-lexicon patterns (keyed by frozenset so they are hashable)
@lru_cache(maxsize=16)
def _get_pattern(lexicon: frozenset[str]) -> re.Pattern[str]:
    if lexicon == DEFAULT_SKILL_LEXICON:
        return _DEFAULT_PATTERN
    return _build_combined_pattern(lexicon)


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

_WHITESPACE_RE = re.compile(r"\s+")


def normalize_skill(skill: str) -> str:
    """
    Normalise a single skill string to its canonical form.

    Steps: strip → collapse whitespace → lowercase → alias lookup.

    >>> normalize_skill("  NodeJS  ")
    'node.js'
    >>> normalize_skill("K8s")
    'kubernetes'
    """
    cleaned = _WHITESPACE_RE.sub(" ", skill.strip()).lower()
    return SKILL_ALIASES.get(cleaned, cleaned)


def normalize_skill_list(skills: Iterable[str] | None) -> list[str]:
    """
    Normalise an iterable of skills, deduplicate, and preserve order.

    >>> normalize_skill_list(["JS", "javascript", "  Python "])
    ['javascript', 'python']
    """
    if not skills:
        return []

    result: list[str] = []
    seen: set[str] = set()

    for raw in skills:
        canonical = normalize_skill(raw)
        if canonical and canonical not in seen:
            seen.add(canonical)
            result.append(canonical)

    return result


def extract_skills_from_text(
    text: str | None,
    *,
    skill_lexicon: Iterable[str] | None = None,
) -> list[str]:
    """
    Extract canonical skills from free text using a single-pass regex scan.

    The function normalises all alias matches before returning, so "k8s"
    in the source text produces ``"kubernetes"`` in the output.

    Skills are returned in order of first appearance in the text.

    Args:
        text:          Free-form text (resume body, job description, etc.).
        skill_lexicon: Override the default lexicon.  Pass ``None`` to use
                       ``DEFAULT_SKILL_LEXICON``.

    Returns:
        Deduplicated list of canonical skill strings, ordered by position.

    >>> "python" in extract_skills_from_text("Experienced Python developer")
    True
    >>> "kubernetes" in extract_skills_from_text("managed k8s clusters")
    True
    """
    if not text:
        return []

    if skill_lexicon is None:
        lexicon = DEFAULT_SKILL_LEXICON
        pattern = _DEFAULT_PATTERN
    else:
        # Build a normalised frozenset so we can cache the compiled pattern
        normalised_lexicon = frozenset(normalize_skill_list(skill_lexicon))
        if not normalised_lexicon:
            return []
        lexicon = normalised_lexicon
        pattern = _get_pattern(lexicon)

    result: list[str] = []
    seen: set[str] = set()

    for match in pattern.finditer(text):
        raw_match = match.group().lower()
        # Resolve through alias table first, then accept as-is if in lexicon
        canonical = SKILL_ALIASES.get(raw_match, raw_match)
        # Collapse internal whitespace variants (e.g. "ci / cd" → "ci/cd")
        canonical = _WHITESPACE_RE.sub(" ", canonical).strip()

        if canonical in lexicon and canonical not in seen:
            seen.add(canonical)
            result.append(canonical)

    return result


def merge_user_skills(
    explicit_skills: Iterable[str] | None,
    resume_text: str | None = None,
    *,
    skill_lexicon: Iterable[str] | None = None,
) -> list[str]:
    """
    Merge explicitly provided skills with skills extracted from free text.

    Explicit skills take priority (appear first); extracted skills fill in
    the rest. All values are normalised and deduplicated.

    Args:
        explicit_skills: Skills the user provided directly (profile tags, etc.).
        resume_text:     Free-form text to mine for additional skills.
        skill_lexicon:   Override the default skill lexicon.

    Returns:
        Merged, deduplicated, ordered list of canonical skill strings.
    """
    explicit = normalize_skill_list(explicit_skills)
    extracted = extract_skills_from_text(resume_text, skill_lexicon=skill_lexicon)

    seen: set[str] = set(explicit)
    merged = list(explicit)

    for skill in extracted:
        if skill not in seen:
            seen.add(skill)
            merged.append(skill)

    return merged