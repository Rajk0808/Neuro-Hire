"""
Resume NLP Extraction Pipeline
================================
Extracts 14 structured fields from raw resume text using a hybrid approach:
  - Regex patterns  → fast, deterministic fields (email, phone, social links)
  - spaCy NER       → name, location (with fallback)
  - LLM (optional)  → semantic fields (skills, experience, education, etc.)
  - Section parsing → header-anchored chunking for structured fields

Optimised for batch throughput: spaCy model loaded once, LLM calls batched.

Changelog vs v1
---------------
  * Phone   : supports +XX-NNN-NNNNNNN format (e.g. Pakistani +92-321-XXXXXXX)
              returns list[str] — all phones captured, not just the first
  * Headers : strips trailing underscore/dash/equals decoration before matching
              (handles "Experience ________" and "CERTIFICATIONS_______" styles)
  * Dates   : adds "currently" / "ongoing" / "today" as end-date alternatives
              and MM/YYYY – MM/YYYY range pattern
  * Skills  : nested sub-section parser strips sub-category prefixes
              (e.g. "Languages & Frameworks: Python, ..." → ["Python", ...])
  * Certs   : pipe-table parser with column-aware continuation and inner-pipe
              edge-case handling (e.g. "MLOps | Machine Learning Operations")
  * Exp     : inline company+location+date parser for single-line job headers
              returns location field separately; description is list[str] bullets
  * Social  : new extract_social_links() — LinkedIn, GitHub, Kaggle, Medium,
              portfolio domain captured from contact header line
  * Schema  : phones → list[str]; social_links → dict added to ResumeData
"""

import re
import json
import logging
from dataclasses import dataclass, field, asdict
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# 1. OUTPUT SCHEMA
# ─────────────────────────────────────────────

@dataclass
class ResumeData:
    name:             Optional[str]  = None
    email:            Optional[str]  = None
    phones:           list[str]      = field(default_factory=list)   # ← was single phone
    location:         Optional[str]  = None
    job_title:        Optional[str]  = None
    social_links:     dict           = field(default_factory=dict)   # ← new
    skills:           list[str]      = field(default_factory=list)
    experience:       list[dict]     = field(default_factory=list)
    education:        list[dict]     = field(default_factory=list)
    certifications:   list[str]      = field(default_factory=list)
    projects:         list[dict]     = field(default_factory=list)
    languages:        list[str]      = field(default_factory=list)
    extracurriculars: list[str]      = field(default_factory=list)
    summary:          Optional[str]  = None
    publications:     list[str]      = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


# ─────────────────────────────────────────────
# 2. REGEX EXTRACTORS  (Layer 1 — fastest)
# ─────────────────────────────────────────────

_EMAIL_RE = re.compile(
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"
)

# FIX: two-alternative phone pattern
#   Alt A — country-code-dash-area-dash-subscriber  e.g. +92-321-1174167
#   Alt B — original pattern with optional parts
_PHONE_RE = re.compile(
    r"""
    (?:(?:\+|00)[1-9]\d{0,2})   # country code  e.g. +92  +1  +44
    [\s\-.]                       # mandatory separator
    \d{3,4}                       # area          e.g. 321  415
    [\s\-.]                       # separator
    \d{7,8}                       # subscriber    e.g. 1174167
    |
    (?:(?:\+|00)[1-9]\d{0,2}[\s\-.])?   # optional country code
    (?:\(?\d{2,4}\)?[\s\-.])?            # optional area code
    \d{3,4}[\s\-.]\d{3,4}               # core number
    (?:\s*(?:ext|x|ext\.)\s*\d{1,6})?   # optional extension
    """,
    re.VERBOSE,
)

# Mapping section header keywords → canonical field names
_SECTION_HEADERS = {
    "summary":          ["professional summary", "summary", "profile", "objective", "about me"],
    "experience":       ["work experience", "experience", "employment", "work history", "career"],
    "education":        ["education", "academic", "qualifications", "degrees"],
    "skills":           ["technical skills", "core competencies", "competencies", "technologies", "skills"],
    "certifications":   ["certifications", "certificates", "credentials", "licenses"],
    "projects":         ["personal projects", "side projects", "portfolio", "projects"],
    "languages":        ["language proficiency", "languages"],
    "extracurriculars": ["extracurricular", "activities", "volunteer", "volunteering", "interests", "hobbies"],
    "publications":     ["publications", "papers", "research", "articles"],
}


def _build_header_pattern() -> re.Pattern:
    all_keywords = [kw for kws in _SECTION_HEADERS.values() for kw in kws]
    joined = "|".join(re.escape(k) for k in sorted(all_keywords, key=len, reverse=True))
    return re.compile(
        rf"^(?:{joined})\s*[:\-–—]?\s*$",
        re.IGNORECASE | re.MULTILINE,
    )

_HEADER_RE = _build_header_pattern()

# FIX: strip trailing decorators before header matching
_DECORATION_RE = re.compile(r"[\s_\-=*]{3,}$")


def _strip_decoration(line: str) -> str:
    """Remove trailing underscore/dash/equals/space decorators from header lines."""
    return _DECORATION_RE.sub("", line).strip()


def extract_email(text: str) -> Optional[str]:
    m = _EMAIL_RE.search(text)
    return m.group(0).lower() if m else None


def extract_phones(text: str) -> list[str]:
    """FIX: return ALL phone numbers found (not just the first)."""
    seen, results = set(), []
    for m in _PHONE_RE.finditer(text[:500]):          # contact header region only
        phone = re.sub(r"\s+", " ", m.group(0)).strip()
        if phone and phone not in seen:
            seen.add(phone)
            results.append(phone)
    return results


def extract_social_links(text: str) -> dict:
    """
    NEW: extract social/portfolio links from the contact header line.
    Returns a dict with keys like: linkedin, github, kaggle, medium, portfolio.
    Handles both full URLs (https://...) and bare domains / keyword tokens.
    """
    result: dict[str, str] = {}
    header = text[:600]   # contact info is always in the first ~600 chars

    # Full URLs
    for m in re.finditer(r"https?://[^\s|,<>]+", header):
        url = m.group(0).rstrip(".,")
        lurl = url.lower()
        if "linkedin" in lurl:   result["linkedin"]  = url
        elif "github" in lurl:   result["github"]    = url
        elif "kaggle" in lurl:   result["kaggle"]    = url
        elif "medium" in lurl:   result["medium"]    = url
        else:                    result.setdefault("portfolio", url)

    # Bare domains  e.g. JillaniPortfolio.com
    for m in re.finditer(r"\b([A-Za-z][A-Za-z0-9\-]+\.(?:com|io|dev|me|net|co))\b", header):
        domain = m.group(1)
        if not any(domain.lower() in v.lower() for v in result.values()):
            result.setdefault("portfolio", domain)

    # Keyword tokens without URL  (e.g. "LinkedIn | GitHub | Kaggle | Medium")
    for kw in ["LinkedIn", "GitHub", "Kaggle", "Medium"]:
        key = kw.lower()
        if key not in result and kw in header:
            result[key] = kw    # present but no URL extracted

    return result


def split_sections(text: str) -> dict[str, str]:
    """
    Split resume text into named sections using header detection.
    FIX: strips trailing underscore/dash decoration before matching.
    Returns { canonical_field: section_text }.
    """
    lines    = text.splitlines()
    sections: dict[str, list[str]] = {}
    current  = "__header__"

    for line in lines:
        stripped     = line.strip()
        stripped_dec = _strip_decoration(stripped)   # ← strip decoration first
        if _HEADER_RE.match(stripped_dec):
            current = _resolve_header(stripped_dec)
            sections.setdefault(current, [])
        else:
            sections.setdefault(current, []).append(line)

    return {k: "\n".join(v).strip() for k, v in sections.items()}


def _resolve_header(header_line: str) -> str:
    clean = re.sub(r"[:\-–—]", "", header_line).strip().lower()
    for canonical, keywords in _SECTION_HEADERS.items():
        for kw in keywords:
            if kw in clean:
                return canonical
    return clean


# ─────────────────────────────────────────────
# 3. spaCy NER LAYER  (Layer 2 — structural)
# ─────────────────────────────────────────────

def _load_spacy():
    """Lazy-load spaCy; returns None if not installed."""
    try:
        import spacy  # noqa: PLC0415
        try:
            return spacy.load("en_core_web_sm")
        except OSError:
            logger.warning(
                "spaCy model 'en_core_web_sm' not found. "
                "Run: python -m spacy download en_core_web_sm"
            )
            return None
    except ImportError:
        logger.warning("spaCy not installed. pip install spacy")
        return None


class SpacyExtractor:
    """Singleton wrapper — loads model once per process."""
    _nlp    = None
    _loaded = False

    @classmethod
    def get(cls):
        if not cls._loaded:
            cls._nlp    = _load_spacy()
            cls._loaded = True
        return cls._nlp

    @classmethod
    def extract(cls, text: str) -> dict:
        nlp    = cls.get()
        result = {"name": None, "location": None, "job_title": None}
        if nlp is None:
            return result

        doc       = nlp(text[:2000])
        persons   = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
        locations = [ent.text for ent in doc.ents if ent.label_ in ("GPE", "LOC")]

        if persons:
            result["name"] = persons[0]
        if locations:
            result["location"] = locations[0]

        return result


# ─────────────────────────────────────────────
# 4. HEURISTIC PARSERS  (Layer 2b — section-level)
# ─────────────────────────────────────────────

def _parse_skills(text: str) -> list[str]:
    """
    FIX: nested sub-section parser.
    Handles sub-category headers like "Programming & Development:" and
    inline prefixes like "• Languages & Frameworks: Python, Keras, ..."
    by stripping the prefix before splitting on commas.
    """
    # Pattern: a sub-category header line (ends with colon, no bullet)
    subsection_header_re = re.compile(r"^[A-Z][^•\n]{3,60}:\s*$")
    # Pattern: inline sub-label prefix "Languages & Frameworks: "
    skill_prefix_re      = re.compile(r"^[A-Z][^:]{3,40}:\s*")

    all_skills: list[str] = []

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or subsection_header_re.match(stripped):
            continue
        # Strip leading bullet/dash/arrow
        stripped = re.sub(r"^[•\-–*►\s]+", "", stripped)
        # Strip inline sub-label prefix
        stripped = skill_prefix_re.sub("", stripped)
        # Split by comma/semicolon
        if any(sep in stripped for sep in [",", ";"]):
            items = re.split(r"[,;]+", stripped)
        else:
            items = [stripped]
        for item in items:
            clean = item.strip().rstrip(".")
            if 2 < len(clean) < 80:
                all_skills.append(clean)

    return all_skills


def _parse_list(text: str) -> list[str]:
    """Generic bullet list parser."""
    lines   = text.splitlines()
    cleaned = [re.sub(r"^[\s•\-–*►\d.]+", "", ln).strip() for ln in lines]
    return [ln for ln in cleaned if len(ln) > 3]


# FIX: date pattern — adds "currently", "ongoing", "today" and MM/YYYY ranges
_DATE_RE = re.compile(
    r"""
    (?:\d{1,2}/\d{4})\s*[-–]\s*(?:\d{1,2}/\d{4}|present|current|currently|now|ongoing|today)
    |\d{4}\s*[-–]\s*(?:\d{4}|present|current|currently|now|ongoing|today)
    |(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|
       Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)
    [\s,]*\d{4}(?:\s*[-–]\s*(?:\d{4}|present|current|currently|now|ongoing|today))?
    |(?:\d{1,2}/\d{4})
    """,
    re.IGNORECASE | re.VERBOSE,
)


def _parse_experience(text: str) -> list[dict]:
    """
    FIX: handles single-line job headers of the form:
        "Title (qualifier)    COMPANY  City, Country  MM/YYYY – MM/YYYY"
    where title, company, location, and date are all on one line separated
    by 3+ spaces (common in PDF-extracted resumes).

    Each entry: { title, company, location, dates, description: list[str] }
    """
    lines   = text.splitlines()
    entries: list[dict] = []
    i       = 0

    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        date_m = _DATE_RE.search(line)
        if date_m:
            before_date = line[: date_m.start()].strip()
            # Split by 3+ spaces to separate title / company / location
            parts    = re.split(r"\s{3,}", before_date)
            title    = parts[0].strip() if parts else before_date
            company  = parts[1].strip() if len(parts) > 1 else None
            location = parts[2].strip() if len(parts) > 2 else None

            # Collect following bullet lines
            bullets: list[str] = []
            j = i + 1
            while j < len(lines):
                nxt = lines[j].strip()
                if not nxt:
                    j += 1
                    continue
                # Stop at next job header (has a date on a non-bullet line)
                if _DATE_RE.search(nxt) and not nxt.startswith(("•", "-", "*")):
                    break
                if nxt.startswith(("•", "-", "*")):
                    bullets.append(re.sub(r"^[•\-*\s]+", "", nxt).strip())
                else:
                    break
                j += 1

            entries.append({
                "title":       title,
                "company":     company,
                "location":    location,
                "dates":       date_m.group(0).strip(),
                "description": bullets,
            })
            i = j
        else:
            i += 1

    return entries


def _parse_education(text: str) -> list[dict]:
    """Parse education blocks: { degree, institution, year, gpa }."""
    gpa_re    = re.compile(r"gpa\s*[:\s]*([\d.]+)", re.IGNORECASE)
    year_re   = re.compile(r"\b(19|20)\d{2}\b")
    degree_kw = re.compile(
        r"\b(b\.?s\.?|b\.?a\.?|m\.?s\.?|m\.?b\.?a\.?|ph\.?d\.?|"
        r"bachelor|master|doctorate|associate|diploma|certificate|"
        r"b\.?e\.?|b\.?tech\.?|m\.?tech\.?|b\.?sc\.?|m\.?sc\.?)\b",
        re.IGNORECASE,
    )

    blocks: list[str] = []
    current: list[str] = []
    for line in text.splitlines():
        if degree_kw.search(line) and current:
            blocks.append("\n".join(current))
            current = [line]
        else:
            current.append(line)
    if current:
        blocks.append("\n".join(current))

    entries: list[dict] = []
    for block in blocks:
        lines  = [ln.strip() for ln in block.splitlines() if ln.strip()]
        if not lines:
            continue
        gpa_m  = gpa_re.search(block)
        year_m = year_re.search(block)
        entries.append({
            "degree":      lines[0],
            "institution": lines[1] if len(lines) > 1 else None,
            "year":        year_m.group(0) if year_m else None,
            "gpa":         gpa_m.group(1)  if gpa_m  else None,
        })
    return entries


def _parse_certifications(text: str) -> list[str]:
    """
    FIX: dual-mode parser.
    Mode A — pipe-table  (e.g. PDF-extracted table with +---+---+ borders)
    Mode B — plain list  (bullet/numbered list fallback)

    Table parser:
      - Detects column count from first border row.
      - Tracks which column each • belongs to, appending continuation lines
        to the correct column's pending cert.
      - Handles inner pipes within cell content (e.g. "MLOps | Operations")
        by using midpoint heuristic to find the true column separator.
    """
    if "+-" in text and "-+" in text:
        return _parse_cert_table(text)
    return _parse_list(text)


def _parse_cert_table(text: str) -> list[str]:
    """Parse 2-column pipe-delimited certification table."""
    col_pending: dict[int, list[str]] = {}
    finished:    list[str]            = []

    def flush_all() -> None:
        for parts in col_pending.values():
            cert = re.sub(r"\s{2,}", " ", " ".join(parts)).strip()
            if len(cert) > 5:
                finished.append(cert)
        col_pending.clear()

    for line in text.splitlines():
        # Border row
        if re.match(r"^\s*\+[-+]+", line):
            flush_all()
            continue

        pipe_positions = [m.start() for m in re.finditer(r"\|", line)]
        if len(pipe_positions) < 2:
            continue

        # Find true column separator using midpoint heuristic
        # (guards against inner pipes like "MLOps | Machine Learning Operations")
        mid             = len(line) // 2
        interior_pipes  = pipe_positions[1:-1]
        if not interior_pipes:
            continue

        col_sep  = min(interior_pipes, key=lambda p: abs(p - mid))
        col0_raw = line[pipe_positions[0] + 1 : col_sep].strip()
        col1_raw = line[col_sep + 1 : pipe_positions[-1]].strip()

        for col_idx, raw in enumerate([col0_raw, col1_raw]):
            if not raw:
                continue
            if raw.startswith("•"):
                # New cert — flush previous in this column
                if col_idx in col_pending:
                    cert = re.sub(r"\s{2,}", " ", " ".join(col_pending[col_idx])).strip()
                    if len(cert) > 5:
                        finished.append(cert)
                col_pending[col_idx] = [raw.lstrip("• ").strip()]
            else:
                # Continuation line
                if col_idx in col_pending:
                    col_pending[col_idx].append(raw)

    flush_all()
    return [c for c in finished if len(c) > 5]


def _parse_projects(text: str) -> list[dict]:
    """Parse project blocks: { name, description, technologies }."""
    tech_re = re.compile(
        r"(?:tech(?:nologies)?|stack|built with|tools?)\s*[:\-]\s*(.+)",
        re.IGNORECASE,
    )
    blocks: list[str] = []
    current: list[str] = []

    for line in text.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith(("•", "-", "*")) and len(stripped) < 80:
            if current:
                blocks.append("\n".join(current))
            current = [line]
        else:
            current.append(line)
    if current:
        blocks.append("\n".join(current))

    entries: list[dict] = []
    for block in blocks:
        lines  = [ln.strip() for ln in block.splitlines() if ln.strip()]
        tech_m = tech_re.search(block)
        if not lines:
            continue
        entries.append({
            "name":         lines[0],
            "description":  " ".join(lines[1:]) if len(lines) > 1 else None,
            "technologies": [t.strip() for t in tech_m.group(1).split(",")] if tech_m else [],
        })
    return entries


# ─────────────────────────────────────────────
# 5. NAME FALLBACK (heuristic)
# ─────────────────────────────────────────────

_COMMON_WORDS = {
    "resume", "curriculum", "vitae", "cv", "profile", "experience",
    "education", "skills", "contact", "summary", "objective",
    "linkedin", "github", "kaggle", "medium", "portfolio",
}

def _heuristic_name(text: str) -> Optional[str]:
    """
    If spaCy misses, try the first non-empty, non-contact-info line
    that looks like a human name (Title Case, 2-4 tokens).
    """
    for line in text.splitlines()[:10]:
        line = line.strip()
        if not line or _EMAIL_RE.search(line) or _PHONE_RE.search(line):
            continue
        # Skip lines that look like contact-info rows (multiple | separators)
        if line.count("|") >= 2:
            continue
        tokens = line.split()
        if 2 <= len(tokens) <= 4:
            if all(t[0].isupper() for t in tokens if t.isalpha()):
                if not any(t.lower() in _COMMON_WORDS for t in tokens):
                    return line
    return None


# ─────────────────────────────────────────────
# 6. CORE PIPELINE
# ─────────────────────────────────────────────

class ResumePipeline:
    """
    Main pipeline. Usage:

        pipeline = ResumePipeline()
        result   = pipeline.extract(resume_text)       # single
        results  = pipeline.batch_extract(texts)       # batch (threaded)
    """

    def __init__(self, max_workers: int = 8):
        self.max_workers = max_workers
        SpacyExtractor.get()   # warm up spaCy on init

    def extract(self, text: str) -> ResumeData:
        """Extract all fields from a single resume text string."""
        data = ResumeData()

        # ── Layer 1: Regex (always runs) ──────────────────────────────────
        data.email        = extract_email(text)
        data.phones       = extract_phones(text)          # FIX: list, all phones
        data.social_links = extract_social_links(text)    # NEW

        # ── Layer 2a: Section splitting ───────────────────────────────────
        sections = split_sections(text)

        # ── Layer 2b: spaCy NER on header region ──────────────────────────
        ner           = SpacyExtractor.extract(text)
        data.name     = ner["name"]     or _heuristic_name(text)
        data.location = ner["location"]
        data.job_title = ner["job_title"]

        # ── Layer 3: Section-aware heuristic parsing ───────────────────────
        if "summary" in sections:
            data.summary = sections["summary"]

        if "skills" in sections:
            data.skills = _parse_skills(sections["skills"])   # FIX: nested parser

        if "experience" in sections:
            data.experience = _parse_experience(sections["experience"])   # FIX: inline

        if "education" in sections:
            data.education = _parse_education(sections["education"])

        if "certifications" in sections:
            data.certifications = _parse_certifications(sections["certifications"])  # FIX: table

        if "projects" in sections:
            data.projects = _parse_projects(sections["projects"])

        if "languages" in sections:
            data.languages = _parse_list(sections["languages"])

        if "extracurriculars" in sections:
            data.extracurriculars = _parse_list(sections["extracurriculars"])

        if "publications" in sections:
            data.publications = _parse_list(sections["publications"])

        # ── Job title fallback ─────────────────────────────────────────────
        if not data.job_title:
            data.job_title = self._infer_job_title(text, data.name)

        return data

    @staticmethod
    def _infer_job_title(text: str, name: Optional[str]) -> Optional[str]:
        title_kw = re.compile(
            r"\b(engineer|developer|manager|analyst|designer|scientist|"
            r"architect|consultant|director|lead|specialist|officer|"
            r"coordinator|executive|intern|associate)\b",
            re.IGNORECASE,
        )
        for line in text.splitlines()[:20]:    # FIX: extended from 15 → 20 lines
            line = line.strip()
            if not line or line == name:
                continue
            if line.count("|") >= 2:           # FIX: skip contact-info rows
                continue
            if title_kw.search(line) and len(line.split()) <= 10:
                return line
        return None

    def batch_extract(self, texts: list[str]) -> list[ResumeData]:
        """
        Process many resumes in parallel using a thread pool.
        spaCy model is shared (read-only) — thread-safe.
        """
        results: list[Optional[ResumeData]] = [None] * len(texts)

        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            futures = {pool.submit(self.extract, text): idx
                       for idx, text in enumerate(texts)}
            for future in as_completed(futures):
                idx = futures[future]
                try:
                    results[idx] = future.result()
                except Exception as exc:
                    logger.error("Failed on resume %d: %s", idx, exc)
                    results[idx] = ResumeData()

        return results   # type: ignore[return-value]