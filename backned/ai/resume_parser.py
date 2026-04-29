from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
import re

import pdfplumber
from docx import Document

from ai.scoring import infer_required_education
from ai.skill_extractor import extract_skills_from_text, normalize_skill_list


SUPPORTED_DOCX_TYPES = {
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
SUPPORTED_PDF_TYPES = {"application/pdf"}

EXPERIENCE_RANGE_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?)\s*(?:-|to)\s*(\d+(?:\.\d+)?)\s*(?:years?|yrs?)\s*(?:of\s+)?experience",
    re.IGNORECASE,
)
EXPERIENCE_SINGLE_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?)\s*(?:\+?\s*)?(?:years?|yrs?)\s*(?:of\s+)?experience",
    re.IGNORECASE,
)
EXPERIENCE_LEVEL_KEYWORDS = {
    "entry": ("fresher", "entry level", "intern"),
    "junior": ("junior", "jr"),
    "mid": ("mid", "mid-level", "intermediate"),
    "senior": ("senior", "sr", "lead"),
}

LOCATION_LINE_PATTERN = re.compile(r"^(location|address)\s*[:\-]\s*(.+)$", re.IGNORECASE)
CITY_STATE_PATTERN = re.compile(r"^[a-zA-Z\s]+,\s*[a-zA-Z\s]+$")


class ResumeParsingError(Exception):
    pass


@dataclass(frozen=True)
class ExperienceProfile:
    years: float | None
    level: str | None


@dataclass(frozen=True)
class ParsedResume:
    raw_text: str
    skills: list[str]
    education_level: str | None
    experience: ExperienceProfile
    location: str | None


def _extract_text_from_pdf(content: bytes) -> str:
    with pdfplumber.open(BytesIO(content)) as pdf:
        pages = [page.extract_text() for page in pdf.pages]

    return "\n".join(filter(None, pages))


def _extract_text_from_docx(content: bytes) -> str:
    document = Document(BytesIO(content))
    paragraphs = [paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()]
    return "\n".join(paragraphs)


def extract_text_from_file(*, filename: str, content_type: str | None, content: bytes) -> str:
    extension = Path(filename).suffix.lower()

    try:
        if extension == ".pdf" or (content_type and content_type in SUPPORTED_PDF_TYPES):
            text = _extract_text_from_pdf(content)
        elif extension == ".docx" or (content_type and content_type in SUPPORTED_DOCX_TYPES):
            text = _extract_text_from_docx(content)
        else:
            raise ResumeParsingError("Unsupported file type. Please upload a PDF or DOCX resume.")
    except ResumeParsingError:
        raise
    except Exception as exc:
        raise ResumeParsingError(
            "Failed to parse the resume file. Please upload a valid PDF or DOCX resume."
        ) from exc

    if not text or not text.strip():
        raise ResumeParsingError("Unable to extract text from the resume. Please upload a readable file.")

    return text


def _extract_experience_years(text: str) -> float | None:
    years: list[float] = []

    for match in EXPERIENCE_RANGE_PATTERN.findall(text):
        start_years, end_years = match
        years.append(max(float(start_years), float(end_years)))

    for match in EXPERIENCE_SINGLE_PATTERN.findall(text):
        years.append(float(match))

    if years:
        return max(years)

    return None


def _infer_experience_level(*, text: str, years: float | None) -> str | None:
    if years is not None:
        if years < 1:
            return "entry"
        if years < 3:
            return "junior"
        if years < 6:
            return "mid"
        return "senior"

    lowered = text.lower()
    for level, keywords in EXPERIENCE_LEVEL_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            return level

    return None


def extract_experience_profile(text: str) -> ExperienceProfile:
    years = _extract_experience_years(text)
    level = _infer_experience_level(text=text, years=years)
    return ExperienceProfile(years=years, level=level)


def extract_location(text: str) -> str | None:
    for line in text.splitlines():
        cleaned = line.strip()
        if not cleaned:
            continue

        match = LOCATION_LINE_PATTERN.match(cleaned)
        if match:
            candidate = match.group(2).strip()
            if 2 <= len(candidate) <= 100:
                return candidate

        if CITY_STATE_PATTERN.match(cleaned) and len(cleaned) <= 60:
            return cleaned

    return None


def parse_resume_text(text: str) -> ParsedResume:
    cleaned_text = re.sub(r"\s+", " ", text).strip()

    skills = normalize_skill_list(extract_skills_from_text(cleaned_text))
    education_level = infer_required_education(cleaned_text)
    experience = extract_experience_profile(cleaned_text)
    location = extract_location(text)

    return ParsedResume(
        raw_text=cleaned_text,
        skills=skills,
        education_level=education_level,
        experience=experience,
        location=location,
    )


def parse_resume_file(*, filename: str, content_type: str | None, content: bytes) -> ParsedResume:
    text = extract_text_from_file(filename=filename, content_type=content_type, content=content)
    return parse_resume_text(text)
