"""
Resume parsing engine.

Responsibilities
----------------
- Extract raw text from PDF and DOCX files robustly.
- Parse structured fields: skills, education level, experience profile, location.
- Expose clean, immutable dataclasses for downstream scoring.

Design principles
-----------------
- All regex patterns compiled once at module level.
- Structured error hierarchy for precise upstream handling.
- Multi-signal location extraction with confidence scoring.
- Experience inference uses both years AND level keywords with priority rules.
- Pure functions throughout — no global state mutation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from io import BytesIO
from pathlib import Path
from typing import Any

import pdfplumber
from pypdf import PdfReader
from docx import Document

from ai.scoring import infer_required_education
from ai.skill_extractor import extract_skills_from_text, normalize_skill_list


# ---------------------------------------------------------------------------
# Supported MIME types
# ---------------------------------------------------------------------------

SUPPORTED_PDF_TYPES: frozenset[str] = frozenset({"application/pdf"})
SUPPORTED_DOCX_TYPES: frozenset[str] = frozenset({
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
})

_EXTENSION_MAP: dict[str, str] = {
    ".pdf":  "pdf",
    ".docx": "docx",
    ".doc":  "docx",
}


# ---------------------------------------------------------------------------
# Experience patterns & ontology
# ---------------------------------------------------------------------------

# "3-5 years of experience", "2 to 4 yrs experience"
_EXP_RANGE_RE = re.compile(
    r"(\d+(?:\.\d+)?)\s*(?:[-–]|to)\s*(\d+(?:\.\d+)?)"
    r"\s*(?:years?|yrs?)\s*(?:of\s+)?(?:experience|exp)?",
    re.IGNORECASE,
)

# "5+ years", "3 years of experience", "2.5 yrs"
_EXP_SINGLE_RE = re.compile(
    r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\s*(?:of\s+)?(?:experience|exp)?",
    re.IGNORECASE,
)

# "1 year experience" (singular without 's')
_EXP_SINGULAR_RE = re.compile(
    r"(\d+(?:\.\d+)?)\s*year\s*(?:of\s+)?(?:experience|exp)",
    re.IGNORECASE,
)

# Ordered from most to least senior so the first match wins
EXPERIENCE_LEVEL_KEYWORDS: dict[str, tuple[str, ...]] = {
    "principal": ("principal engineer", "staff engineer", "distinguished engineer"),
    "lead":      ("tech lead", "team lead", "lead engineer", "lead developer"),
    "senior":    ("senior", "sr.", "sr "),
    "mid":       ("mid-level", "mid level", "intermediate"),
    "junior":    ("junior", "jr.", "jr "),
    "entry":     ("fresher", "entry level", "entry-level", "graduate trainee", "trainee"),
    "intern":    ("intern", "internship", "apprentice"),
}

# Years → canonical level mapping (upper-bound exclusive)
_YEARS_TO_LEVEL: list[tuple[float, str]] = [
    (0.5,  "intern"),
    (1.5,  "entry"),
    (3.0,  "junior"),
    (6.0,  "mid"),
    (10.0, "senior"),
    (14.0, "lead"),
    (float("inf"), "principal"),
]


# ---------------------------------------------------------------------------
# Location patterns
# ---------------------------------------------------------------------------

# "Location: Bangalore, India"  /  "Address: New York, NY"
_LOCATION_LABEL_RE = re.compile(
    r"^(?:location|address|city|based\s+in|residing\s+in)\s*[:\-]\s*(.+)$",
    re.IGNORECASE,
)

# "Bangalore, Karnataka"  /  "New York, NY"
_CITY_STATE_RE = re.compile(
    r"^[A-Za-z][A-Za-z\s\-\.]{1,40},\s*[A-Za-z][A-Za-z\s]{1,30}$"
)

# Known remote indicators
_REMOTE_TOKENS: frozenset[str] = frozenset({
    "remote", "work from home", "wfh", "hybrid", "anywhere",
    "pan india", "open to relocation",
})

# Section headers that signal we've moved past the contact block
_SECTION_BREAK_RE = re.compile(
    r"^(?:objective|summary|profile|experience|education|skills|projects|"
    r"certifications|publications|references)\b",
    re.IGNORECASE,
)

# Noise lines that look like locations but aren't
_NOISE_RE = re.compile(
    r"(?:university|college|school|institute|ltd|pvt|inc|corp|technologies|solutions)",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Error hierarchy
# ---------------------------------------------------------------------------

class ResumeParsingError(Exception):
    """Base class for all resume-parsing failures."""


class UnsupportedFileTypeError(ResumeParsingError):
    """Raised when the uploaded file format is not PDF or DOCX."""


class EmptyResumeError(ResumeParsingError):
    """Raised when the file parses successfully but yields no usable text."""


class CorruptFileError(ResumeParsingError):
    """Raised when the file is structurally invalid or unreadable."""


# ---------------------------------------------------------------------------
# Immutable dataclasses
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ExperienceProfile:
    """
    Structured representation of a candidate's (or posting's) experience.

    Both fields are optional; downstream scorers handle every combination.
    """
    years: float | None = None
    level: str | None   = None


@dataclass(frozen=True)
class ParsedResume:
    """
    Complete structured output of the resume parser.

    All fields are derived from ``raw_text``; no external data is injected.
    """
    raw_text:        str
    skills:          list[str]
    education_level: str | None
    experience:      ExperienceProfile
    location:        str | None

    # Diagnostic metadata — useful for logging & debugging
    location_source: str | None = field(default=None)  # "label" | "city_state" | "remote"
    page_count:      int | None = field(default=None)   # PDF only


# ---------------------------------------------------------------------------
# Text extraction
# ---------------------------------------------------------------------------

def _extract_text_from_pdf(content: bytes) -> tuple[str, int]:
    """
    Extract all text from a PDF, returning ``(text, page_count)``.

    Strategy
    --------
    1. Try ``pdfplumber`` (best for layout preservation).
    2. Fall back to ``pypdf`` if ``pdfplumber`` returns empty text (handles
       different encodings / corruptions).
    3. Check for images on pages; if text is empty but images exist, it's likely
       a scanned document.
    """
    try:
        stream = BytesIO(content)
        text_parts: list[str] = []
        page_count = 0
        has_images = False

        # Attempt 1: pdfplumber
        with pdfplumber.open(stream) as pdf:
            page_count = len(pdf.pages)
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                if not page_text.strip():
                    # Columnar / layout-heavy fallback
                    page_text = page.extract_text(layout=True) or ""
                
                if page_text.strip():
                    text_parts.append(page_text)
                
                if not has_images and getattr(page, "images", None):
                    has_images = True

        # Attempt 2: pypdf fallback if Attempt 1 yielded nothing
        if not "".join(text_parts).strip():
            stream.seek(0)
            reader = PdfReader(stream)
            page_count = len(reader.pages)
            for page in reader.pages:
                page_text = page.extract_text() or ""
                if page_text.strip():
                    text_parts.append(page_text)
                
                if not has_images and page.images:
                    has_images = True

        full_text = "\n".join(text_parts).strip()

        if not full_text and has_images:
            raise EmptyResumeError(
                "No readable text could be extracted, but images were detected. "
                "This PDF appears to be a scanned image. Please use a text-based "
                "PDF or OCR the document before uploading."
            )

        return full_text, page_count

    except ResumeParsingError:
        raise
    except Exception as exc:
        raise CorruptFileError(
            "The PDF file appears to be corrupt or password-protected. "
            "Please upload a readable, unlocked PDF."
        ) from exc


def _extract_text_from_docx(content: bytes) -> str:
    """
    Extract all paragraph and table text from a DOCX file.

    Tables are a common source of skills / experience data that the naive
    paragraph-only approach silently drops.
    """
    try:
        doc = Document(BytesIO(content))
        parts: list[str] = []

        for para in doc.paragraphs:
            stripped = para.text.strip()
            if stripped:
                parts.append(stripped)

        # Tables often contain skills/experience in grids
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    stripped = cell.text.strip()
                    if stripped and stripped not in parts:
                        parts.append(stripped)

        # Headers and Footers often contain contact info
        for section in doc.sections:
            for header in [section.header, section.footer]:
                if not header:
                    continue
                for para in header.paragraphs:
                    stripped = para.text.strip()
                    if stripped and stripped not in parts:
                        parts.append(stripped)

        return "\n".join(parts)

    except Exception as exc:
        raise CorruptFileError(
            "The DOCX file appears to be corrupt or in an unsupported format. "
            "Please upload a valid .docx resume."
        ) from exc


def extract_text_from_file(
    *,
    filename:     str,
    content_type: str | None,
    content:      bytes,
) -> tuple[str, dict[str, Any]]:
    """
    Dispatch to the correct extractor based on extension + MIME type.

    Returns ``(raw_text, metadata)`` where *metadata* may include
    ``page_count`` for PDFs.

    Raises
    ------
    UnsupportedFileTypeError
        When neither the extension nor the MIME type is recognised.
    EmptyResumeError
        When parsing succeeds but yields no usable text.
    CorruptFileError
        When the file is structurally invalid.
    """
    extension = Path(filename).suffix.lower()
    fmt = _EXTENSION_MAP.get(extension)

    if fmt is None and content_type:
        if content_type in SUPPORTED_PDF_TYPES:
            fmt = "pdf"
        elif content_type in SUPPORTED_DOCX_TYPES:
            fmt = "docx"

    if fmt is None:
        raise UnsupportedFileTypeError(
            f"Unsupported file type '{extension or content_type}'. "
            "Please upload a PDF (.pdf) or Word document (.docx)."
        )

    metadata: dict[str, Any] = {}

    if fmt == "pdf":
        text, page_count = _extract_text_from_pdf(content)
        metadata["page_count"] = page_count
    else:
        text = _extract_text_from_docx(content)

    if not text or not text.strip():
        raise EmptyResumeError(
            "No readable text could be extracted from the resume. "
            "If the file uses scanned images, please use a text-based PDF."
        )

    return text, metadata


# ---------------------------------------------------------------------------
# Experience extraction
# ---------------------------------------------------------------------------

def _extract_experience_years(text: str) -> float | None:
    """
    Extract the *maximum* years figure mentioned in the text.

    Priority: range patterns > single patterns > singular patterns.
    Taking the maximum handles "3–5 years" (we take 5) which represents
    the upper bound of what a candidate might claim.
    """
    years: list[float] = []

    for lo, hi in _EXP_RANGE_RE.findall(text):
        years.append(max(float(lo), float(hi)))

    for val in _EXP_SINGLE_RE.findall(text):
        years.append(float(val))

    for val in _EXP_SINGULAR_RE.findall(text):
        years.append(float(val))

    # Sanity-clamp: ignore implausible values (> 60 years)
    years = [y for y in years if 0 <= y <= 60]

    return max(years) if years else None


def _years_to_level(years: float) -> str:
    """Map a concrete years figure to a canonical experience level."""
    for threshold, level in _YEARS_TO_LEVEL:
        if years < threshold:
            return level
    return "principal"


def _infer_level_from_keywords(text: str) -> str | None:
    """
    Scan text for level keywords, returning the highest match found.

    Scans from most-senior to least-senior so that "Senior React Developer"
    resolves to ``senior`` rather than stopping at a junior keyword embedded
    elsewhere.
    """
    lowered = text.lower()
    for level, keywords in EXPERIENCE_LEVEL_KEYWORDS.items():
        if any(kw in lowered for kw in keywords):
            return level
    return None


def extract_experience_profile(text: str) -> ExperienceProfile:
    """
    Build an ``ExperienceProfile`` from free-form text.

    Strategy
    --------
    1. Extract numeric years (most reliable signal).
    2. Derive level from years via ``_YEARS_TO_LEVEL`` if years are found.
    3. If no years found, fall back to keyword-based level inference.
    4. Override level with keyword inference when the keyword signals a
       *higher* seniority than years alone would suggest (e.g. "Senior
       Developer with 2 years" → keep ``senior``).
    """
    years = _extract_experience_years(text)

    level_from_years    = _years_to_level(years) if years is not None else None
    level_from_keywords = _infer_level_from_keywords(text)

    if level_from_years and level_from_keywords:
        # Prefer whichever signal implies a higher seniority
        rank_years    = list(EXPERIENCE_LEVEL_KEYWORDS).index(level_from_years)   if level_from_years    in EXPERIENCE_LEVEL_KEYWORDS else 999
        rank_keywords = list(EXPERIENCE_LEVEL_KEYWORDS).index(level_from_keywords) if level_from_keywords in EXPERIENCE_LEVEL_KEYWORDS else 999
        level = level_from_years if rank_years <= rank_keywords else level_from_keywords
    else:
        level = level_from_years or level_from_keywords

    return ExperienceProfile(years=years, level=level)


# ---------------------------------------------------------------------------
# Location extraction
# ---------------------------------------------------------------------------

def extract_location(text: str) -> tuple[str | None, str | None]:
    """
    Extract a candidate's location from resume text.

    Returns ``(location_string, source)`` where *source* is one of:
    ``"label"``, ``"city_state"``, ``"remote"``, or ``None``.

    Strategy
    --------
    1. Scan only the first 40 lines (contact block) for labelled location
       fields ("Location: …", "Address: …").
    2. Fall back to heuristic city/state pattern matching on the same block.
    3. Detect remote-work indicators anywhere in the document.

    Stops scanning after the first section-header line (Experience,
    Education, etc.) to avoid false positives from job history addresses.
    """
    lines = text.splitlines()
    contact_lines: list[str] = []

    for line in lines[:60]:
        stripped = line.strip()
        if not stripped:
            continue
        if _SECTION_BREAK_RE.match(stripped):
            break
        contact_lines.append(stripped)

    # Pass 1 – explicit label
    for line in contact_lines:
        m = _LOCATION_LABEL_RE.match(line)
        if m:
            candidate = m.group(1).strip()
            if 2 <= len(candidate) <= 120 and not _NOISE_RE.search(candidate):
                return candidate, "label"

    # Pass 2 – city/state heuristic
    for line in contact_lines:
        if _CITY_STATE_RE.match(line) and not _NOISE_RE.search(line):
            return line, "city_state"

    # Pass 3 – remote indicator (full document scan)
    full_lower = text.lower()
    for token in _REMOTE_TOKENS:
        if token in full_lower:
            return token.title(), "remote"

    return None, None


# ---------------------------------------------------------------------------
# High-level parsers
# ---------------------------------------------------------------------------

def parse_resume_text(text: str) -> ParsedResume:
    """
    Parse structured fields from raw resume text.

    This is the core parsing function. All other ``parse_*`` entry points
    ultimately call this after extracting text from a file.

    Args:
        text: Raw text extracted from a resume file.

    Returns:
        ``ParsedResume`` with skills, education, experience, and location.
    """
    # Normalise whitespace for NLP passes; keep original for location
    cleaned = re.sub(r"[ \t]+", " ", text).strip()   # collapse horizontal WS only
    # (vertical whitespace preserved so line-based location extraction still works)

    skills          = normalize_skill_list(extract_skills_from_text(cleaned))
    education_level = infer_required_education(cleaned)
    experience      = extract_experience_profile(cleaned)
    location, loc_source = extract_location(text)   # use raw text for lines

    return ParsedResume(
        raw_text=cleaned,
        skills=skills,
        education_level=education_level,
        experience=experience,
        location=location,
        location_source=loc_source,
    )


def parse_resume_file(
    *,
    filename:     str,
    content_type: str | None,
    content:      bytes,
) -> ParsedResume:
    """
    End-to-end entry point: bytes → ``ParsedResume``.

    Extracts text from the uploaded file, then delegates to
    ``parse_resume_text`` for structured field parsing.

    Args:
        filename:     Original filename (used to infer format from extension).
        content_type: MIME type from the HTTP upload (may be ``None``).
        content:      Raw file bytes.

    Returns:
        Fully populated ``ParsedResume``.

    Raises:
        UnsupportedFileTypeError: Unrecognised file format.
        EmptyResumeError:         File parsed but contained no text.
        CorruptFileError:         File is structurally invalid.
    """
    text, metadata = extract_text_from_file(
        filename=filename,
        content_type=content_type,
        content=content,
    )
    resume = parse_resume_text(text)

    # Attach file-level metadata that parse_resume_text cannot know
    return ParsedResume(
        raw_text=resume.raw_text,
        skills=resume.skills,
        education_level=resume.education_level,
        experience=resume.experience,
        location=resume.location,
        location_source=resume.location_source,
        page_count=metadata.get("page_count"),
    )